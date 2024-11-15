import pandas as pd
import numpy as np
import datetime
from colorama import Fore, Style
import itertools


def compare_empty_dataframes(df1, df2):
    """Check if both DataFrames are empty and have the same columns."""
    return df1.empty and df2.empty and df1.columns.equals(df2.columns)


def dataframe_compare(df1, df2, diff_file, columnsort):
    """Compare two dataframes and output differences."""
    if compare_empty_dataframes(df1, df2):
        return True, 0

    if not compare_empty_dataframes(df1, df2):
        if len(df1.index) == len(df2.index) and len(df1.columns) == len(df2.columns):
            current_time = datetime.datetime.now()

            # Clean and preprocess DataFrames
            for df in [df1, df2]:
                df.columns = df.columns.str.strip()  # Ensure column names are clean
                df.replace(["NA", "N/A", np.nan], "", inplace=True)

            # Sort DataFrames
            df1.sort_index(axis=1, inplace=True)
            df2.sort_index(axis=1, inplace=True)
            df1.sort_values(by=columnsort, inplace=True)
            df2.sort_values(by=columnsort, inplace=True)
            df1.reset_index(drop=True, inplace=True)
            df2.reset_index(drop=True, inplace=True)

            # Initialize variables for chunk processing
            chunksize = 100000  # Adjust based on memory limitations
            diff_chunks = []
            num_chunks = len(df1) // chunksize + 1

            for chunk_idx in range(num_chunks):
                # Get chunk indices
                start_idx = chunk_idx * chunksize
                end_idx = min((chunk_idx + 1) * chunksize, len(df1))

                # Extract chunks
                chunk1 = df1.iloc[start_idx:end_idx].copy()
                chunk2 = df2.iloc[start_idx:end_idx].copy()

                # Add metadata columns
                chunk1["Row#"] = range(start_idx + 1, end_idx + 1)
                chunk2["Row#"] = range(start_idx + 1, end_idx + 1)
                chunk1["Files"] = "src_df"
                chunk2["Files"] = "db_df"

                # Identify columns to compare
                common_columns = chunk1.columns.intersection(chunk2.columns)
                columns_to_compare = common_columns.difference(["Row#", "Files"])

                # Compare chunks
                chunk_diff = chunk1[columns_to_compare].ne(chunk2[columns_to_compare])
                none_comparison = (chunk1[columns_to_compare].isnull()) & (
                    chunk2[columns_to_compare].isnull()
                )
                chunk_diff = chunk_diff[~none_comparison]  # Exclude None matches

                # Identify rows with any differences
                any_diff = chunk_diff.any(axis=1)

                # Add columns showing differences
                chunk1["Columns_diff"] = chunk_diff.apply(
                    lambda row: ", ".join(row.index[row]), axis=1
                )
                chunk2["Columns_diff"] = chunk_diff.apply(
                    lambda row: ", ".join(row.index[row]), axis=1
                )

                # Combine differences from src_df and db_df
                chunk_diff_filtered = pd.concat(
                    [chunk1[any_diff], chunk2[any_diff]], ignore_index=True
                )
                diff_chunks.append(chunk_diff_filtered)

            # Combine all difference chunks
            if diff_chunks:
                df_diff_sorted = pd.concat(diff_chunks, ignore_index=True)
                df_diff_sorted.sort_values(
                    by=["Row#", "Files"], inplace=True, ascending=[True, True]
                )
                df_diff_sorted.reset_index(drop=True, inplace=True)

                # Save differences to file
                try:
                    df_diff_sorted.to_csv(diff_file, index=False, sep="|")
                except Exception as e:
                    print(f"Error saving diff file: {e}")
                    return False, []

                # Print sample differences
                num_records_with_diff = len(df_diff_sorted)
                print(
                    Fore.GREEN
                    + f"Total differences: {num_records_with_diff}"
                    + Style.RESET_ALL
                )

                print(
                    Fore.RED
                    + "\nSample differences (first 10 lines):"
                    + Style.RESET_ALL
                )
                try:
                    with open(diff_file, "r") as f:
                        for line in itertools.islice(f, 10):
                            print(line.strip())
                except Exception as e:
                    print(f"Error reading diff file: {e}")

                return False, set(df_diff_sorted["Columns_diff"])
            else:
                print(Fore.GREEN + "No differences found." + Style.RESET_ALL)
                return True, 0
        else:
            print(
                Fore.RED
                + f"DataFrames are not identical: Rows (df1={len(df1.index)}, df2={len(df2.index)}), "
                f"Columns (df1={len(df1.columns)}, df2={len(df2.columns)})"
                + Style.RESET_ALL
            )
            return False, 0


# Example usage:
# df1 = pd.read_csv("file1.csv")
# df2 = pd.read_csv("file2.csv")
# dataframe_compare(df1, df2, "differences.csv", "id_column")
