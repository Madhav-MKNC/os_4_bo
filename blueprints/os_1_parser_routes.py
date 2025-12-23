from flask import Blueprint, render_template, request, url_for, redirect
from pathlib import Path
import os

from configs import UPLOAD_FOLDER, OUTPUT_FOLDER
from os_1_parser.main import utils, ms_office, process_addresses, phone_number_lookup


os_1_parser_routes = Blueprint('os_1_parser_routes', __name__)


def _run_text_to_xlsx_with_flags(flag: str, text_path: str, out_dir: str, enable_sorting: bool | None) -> str:
    file_text = utils.read_input_file(text_path)
    address_list = process_addresses(file_text, flag=flag, enable_sorting=enable_sorting)
    out_xlsx = utils.generate_output_file_path(out_dir, Path(text_path).stem, "xlsx")
    ms_office.export_to_MS_Excel_using_xlsxwriter(address_list=address_list, file_name=out_xlsx)
    return out_xlsx


def load_lookup_from_upload(file_storage) -> list[int]:
    """Read uploaded phone_number_lookup .txt and return cleaned list of strings."""
    raw = file_storage.read().decode("utf-8", errors="ignore")
    # split lines, strip, drop empties, keep unique while preserving order
    seen, out = set(), []
    for line in raw.splitlines():
        s = line.strip()
        if not s: 
            continue
        if s not in seen:
            seen.add(int(s))
            out.append(int(s))
    return out


def write_lookup_file(output_folder):
    """Creates phone_number_lookup.txt from phone_number_lookup.numbers."""
    filepath = Path(output_folder) / "phone_number_lookup.txt"
    numbers = list(map(str, phone_number_lookup.new_numbers))

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(numbers))

    return filepath


@os_1_parser_routes.route("/os1_phone", methods=["GET", "POST"])
def os1_phone():
    if request.method == "POST":
        flag = request.form.get("flag")
        if flag not in ["-f", "-m"]:
            return "Invalid flag", 400

        sort_choice = request.form.get("enable_sorting")
        enable_sorting = True if sort_choice == "on" else False

        uploaded_lookup = request.files.get("phone_lookup")
        if uploaded_lookup and uploaded_lookup.filename and uploaded_lookup.filename.endswith(".txt"):
            phone_number_lookup.numbers = load_lookup_from_upload(uploaded_lookup)
        else:
            phone_number_lookup.numbers = []

        # required main input (.txt)
        main_file = request.files.get("main_file")
        if not main_file or not main_file.filename.endswith(".txt"):
            return "Upload a .txt main file", 400

        main_path = os.path.join(UPLOAD_FOLDER, main_file.filename)
        main_file.save(main_path)

        try:
            out_xlsx = _run_text_to_xlsx_with_flags(
                flag=flag,
                text_path=main_path,
                out_dir=OUTPUT_FOLDER,
                enable_sorting=enable_sorting
            )

            # write lookup file (from uploaded list OR empty)
            lookup_path = write_lookup_file(OUTPUT_FOLDER)

            files = [os.path.basename(out_xlsx), lookup_path.name]
            return redirect(url_for("processing_and_pre_processing_routes.show_results", files=",".join(files)))

        except Exception as e:
            return f"Error: {e}", 500

    return render_template("os1_phone.html")

