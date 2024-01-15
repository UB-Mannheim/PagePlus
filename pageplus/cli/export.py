from typing import List, Optional
from pathlib import Path
import csv

from rich.progress import track
from shapely import LineString
import typer
from typing_extensions import Annotated

from pageplus.io.logger import logging
from pageplus.io.utils import collect_xml_files, determine_output_path
from pageplus.models.page import Page

app = typer.Typer()

@app.command()
def fulltext(
    inputs: Annotated[List[Path], typer.Argument(exists=True, help="Iterable of paths to the PAGE XML files.")],
    outputdir: Annotated[Optional[Path], typer.Option(help="Path to the output directory where the text files will be saved. If not specified, an output directory named Fulltext will be created in each input file’s parent directory.")]= None
):
    """
    Extracts full text from PAGE XML files and saves it as text files.

    Iterates over each specified PAGE XML file, extracts the text while dehyphenating it, and writes
    the resulting text to a specified or default output directory.

    Args:
        inputs: Iterable of paths to the PAGE XML files.
        outputdir: Path to the output directory where the text files will be saved.
    """
    # Collect XML files from the input paths
    xml_files = collect_xml_files(map(Path, inputs))
    if not xml_files:
        raise FileNotFoundError('No XML files found in the input directory.')

    # Process each XML file
    for xml_file in track(xml_files, description="Extracting fulltext.." ):
        filename = xml_file.stem  # Extracts the filename without the extension
        logging.info(f'Processing file: {filename}')

        # Determine the output file path
        text_output_path = Path(f"{xml_file.parent}/Fulltext/{xml_file.with_suffix('.txt').name}") if outputdir is None \
            else outputdir / filename
        text_output_path.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f'Writing text file to: {text_output_path}')

        # Extract and write full text to the output file
        with open(text_output_path, 'w') as fout:
            extracted_text = Page(xml_file).extract_fulltext(dehyphenate=True)
            fout.write(extracted_text)


@app.command()
def dsv(
    inputs: Annotated[List[Path], typer.Argument(exists=True, help="Iterable of paths to the PAGE XML files.")],
    outputdir: Annotated[Optional[Path], typer.Option(help="Filename of the output directory. Default is creating an output directory, called PagePlusOutput, in the input directory.")]= None,
    delimiter: Annotated[str, typer.Option(help="Delimiter to use for separating values")] = '\t',
    dehyphenate: Annotated[bool, typer.Option(help="Dehyphenate the textlines (no impact on coordinates)")]= True
):
    """
    Extracts text and coordinates from PAGE XML files and saves them as delimiter-separated values (DSV) files.

    Processes each PAGE XML file, extracts text line information including coordinates, and writes
    them to a DSV file with the specified delimiter.

    Args:
        inputs: Iterable of paths to the PAGE XML files.
        delimiter: The delimiter to use in the DSV file.
        dehyphenate: If True, dehyphenates the text lines in the output.
        outputdir: Path to the output directory where the DSV files will be saved.
    """
    # You
    xml_files = collect_xml_files(map(Path, inputs))
    # raise error if no xml files are found
    if not xml_files:
        raise FileNotFoundError('No xml files found in input directory')

    # loop through all xml files
    for xml_file in track(xml_files, description="Exporting data to a DSV file.."):
        # get filename
        filename = xml_file.name
        page = Page(xml_file)
        logging.info('Processing file: ' + filename)

        line_infos = {'id': [], 'text': [], 'region': [],
                      'start': [], 'mean': [], 'end': [],
                      'area': [], 'width': [], 'length': []}
        for rid, textregion in enumerate(page.regions.textregions):
            for line in textregion.textlines:
                if line.get_text is None: continue
                line_infos['id'].append(line.get_id())
                line_infos['text'].append(line.get_text())
                line_infos['region'].append(rid)
                baseline_coords = line.get_baseline_coordinates(returntype='linestring')
                if baseline_coords is not None:
                    line_infos['start'].append([int(baseline_coords.bounds[0]), int(baseline_coords.bounds[1])])
                    line_infos['mean'].append([int(baseline_coords.centroid.x), int(baseline_coords.centroid.y)])
                    line_infos['end'].append([int(baseline_coords.bounds[2]), int(baseline_coords.bounds[3])])
                else:
                    line_infos['start'].append([-1, -1])
                    line_infos['mean'].append([-1, -1])
                    line_infos['end'].append([-1, -1])
                textline_coords = line.get_coordinates(returntype='mrr')
                if textline_coords is not None:
                    lines = sorted([LineString([c1, c2]) for c1, c2 in zip(textline_coords.exterior.coords[:-1],
                                                                           textline_coords.exterior.coords[1:])],
                                   key=lambda x: x.length)
                    line_infos['area'].append(int(textline_coords.area))
                    line_infos['width'].append(int(lines[0].length))
                    line_infos['length'].append(int(lines[-1].length))
                else:
                    line_infos['area'].append(-1)
                    line_infos['width'].append(-1)
                    line_infos['length'].append(-1)

        if dehyphenate:
            line_infos['text'] = page.dehyphe(line_infos['text'])

        # Write to file
        filepath = Path(f"{xml_file.parent}/TSV/{xml_file.with_suffix('.tsv').name}") if outputdir is None \
            else outputdir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        logging.info('Wrote separated value file to output directory: ' + str(filepath))
        with open(filepath, 'w') as tsvfile:
            #csv writer to write in tsv file
            tsv_writer = csv.writer(tsvfile, delimiter=delimiter)
            #write header in tsv file
            tsv_writer.writerow(line_infos.keys())
            #write rows
            tsv_writer.writerows(zip(*line_infos.values()))
            #close csv file
            tsvfile.close()


if __name__ == "__main__":
    app()
