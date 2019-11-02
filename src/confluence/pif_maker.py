

def create_pif(headers, row):

    print(headers)
    print(row)

    # chemical_system = ChemicalSystem()
    # chemical_system.chemical_formula = 'MgO2'
    #
    # band_gap = Property()
    # band_gap.name = 'Band gap'
    # band_gap.scalars = 7.8
    # band_gap.units = 'eV'
    #
    # chemical_system.properties = band_gap


def convert(files=[], **kwargs):
    """
    Converts a specialized CSV/TSV file to a physical information file.

    :param files: list of files to convert
    :return: yields PIFs created from the input files
    """

    table = convert_df_to_table(input_file)

    input_file.seek(0)

    for i, row in enumerate(table):

        if not any(row):
            continue

        if i == 0:
            headers = row
        else:
            row_pif = create_pif(headers, row)
            yield row_pif
