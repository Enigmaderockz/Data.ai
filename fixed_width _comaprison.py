def format_fixed_width_row(row, column_widths):
  formatted_row = []
  start = 0
  for width in column_widths:
    end = start + width
    formatted_row.append(row[start:end].strip())
    start = end
  return '|'.join(formatted_row)


def generate_column_widths(width_details):
  column_widths = []
  for column_info in width_details[1:]:
    start, end = int(column_info[1]), int(column_info[2])
    width = end - start + 1
    column_widths.append(width)
  return column_widths


width_details = [['Column', 'Start', 'End'], ['CHG_IND', '1', '1'],
                 ['KEY_ACCT', '2', '27'], ['NUM_CLI_FCNG_ACCT', '28', '59'],
                 ['NUM_OFC', '60', '69'], ['NUM_ACCT', '70', '94'],
                 ['NUM_FA', '95', '104'], ['CDE_ACCT_TYP', '105', '136'],
                 ['CDE_ACCT_STA', '137', '168'],
                 ['CDE_ACCT_APPR_STA', '169', '193'],
                 ['DT2_ACCT_OPEN', '194', '203'],
                 ['DT2_ACCT_CLOSE', '204', '213'],
                 ['DT2_ACCT_REOPEN', '214', '223'],
                 ['CDE_ACCT_ENTY', '224', '248'], ['CDE_INST', '249', '273'],
                 ['CDE_ACCT_PRD_TYP', '274', '282'],
                 ['MANAGED_ACCT_IND', '283', '308'], ['FILLER', '309', '825']]

column_widths = generate_column_widths(width_details)

with open('b.csv', 'r') as input_file, open('formatted_b.csv',
                                            'w') as output_file:
  # Skip the first line (header) in b.csv
  next(input_file)

  for line in input_file:
    # Stop processing when reaching the last line (ignoring it)
    if line.strip() == 't-sfsfsfsf':
      break

    formatted_line = format_fixed_width_row(line, column_widths)
    output_file.write(formatted_line + '\n')
