def fill_missing_months(df):
    df = df.copy()  # Avoid SettingWithCopyWarning
    df['YearMonth'] = df['Created'].dt.to_period('M').dt.to_timestamp()
    grouped = df.groupby('YearMonth').size().reset_index(name='Count')
    full_range = pd.date_range(grouped['YearMonth'].min(), grouped['YearMonth'].max(), freq='MS')
    full_df = pd.DataFrame({'YearMonth': full_range})
    merged = full_df.merge(grouped, on='YearMonth', how='left').fillna(0)
    merged['Count'] = merged['Count'].astype(int)
    return merged
