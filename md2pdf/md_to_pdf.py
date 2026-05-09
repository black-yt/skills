import os
import sys

import markdown2
from weasyprint import HTML


def md_to_pdf(md_path, pdf_path, base_path=None):
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown2.markdown(md_content, extras=["tables", "fenced-code-blocks"])

    css_style = """
    <style>
    img { max-width: 100%; height: auto; }
    table { border-collapse: collapse; }
    table, th, td { border: 1px solid black; }
    th, td { padding: 4px; }
    </style>
    """
    html_content = css_style + html_content

    if base_path:
        html_content = html_content.replace('src="', f'src="{base_path}/')

    HTML(string=html_content, base_url=base_path or ".").write_pdf(pdf_path)
    print(f"已生成 PDF: {pdf_path}")


def main():
    if len(sys.argv) < 3:
        print("用法: python md_to_pdf.py <markdown路径> <输出pdf路径> [起始路径]")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2]
    base_dir = sys.argv[3] if len(sys.argv) >= 4 else None

    if os.path.isdir(pdf_file):
        pdf_file = os.path.join(
            pdf_file,
            os.path.splitext(os.path.basename(md_file))[0] + ".pdf",
        )

    md_to_pdf(md_file, pdf_file, base_dir)


if __name__ == "__main__":
    main()
