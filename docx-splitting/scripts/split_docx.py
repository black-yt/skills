import argparse
import math
import os

import win32com.client as win32


def split_docx_lossless_by_pages(input_path, output_dir="split_output", parts=4):
    input_path = os.path.abspath(input_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0

    try:
        doc = word.Documents.Open(input_path)

        doc.Repaginate()
        total_pages = doc.ComputeStatistics(2)  # 2 = wdStatisticPages

        pages_per_part = math.ceil(total_pages / parts)

        print(f"总页数: {total_pages}")
        print(f"每份约: {pages_per_part} 页")

        for i in range(parts):
            start_page = i * pages_per_part + 1
            end_page = min((i + 1) * pages_per_part, total_pages)

            if start_page > total_pages:
                break

            start_range = word.Selection.GoTo(
                What=1,      # wdGoToPage
                Which=1,     # wdGoToAbsolute
                Count=start_page,
            )
            start_pos = start_range.Start

            if end_page < total_pages:
                end_range = word.Selection.GoTo(
                    What=1,
                    Which=1,
                    Count=end_page + 1,
                )
                end_pos = end_range.Start
            else:
                end_pos = doc.Content.End

            part_range = doc.Range(start_pos, end_pos)

            new_doc = word.Documents.Add()
            new_doc.Range().FormattedText = part_range.FormattedText

            output_path = os.path.join(output_dir, f"part_{i + 1}.docx")
            new_doc.SaveAs2(output_path, FileFormat=16)  # 16 = docx
            new_doc.Close(False)

            print(f"已保存: {output_path}，页码 {start_page}-{end_page}")

        doc.Close(False)

    finally:
        word.Quit()


def main():
    parser = argparse.ArgumentParser(description="Split a DOCX file into page-based parts using Microsoft Word COM.")
    parser.add_argument("input_path", help="Path to the input .docx file.")
    parser.add_argument("--output-dir", default="split_output", help="Directory for generated .docx parts.")
    parser.add_argument("--parts", type=int, default=4, help="Number of parts to split into.")
    args = parser.parse_args()

    split_docx_lossless_by_pages(
        args.input_path,
        output_dir=args.output_dir,
        parts=args.parts,
    )


if __name__ == "__main__":
    main()
