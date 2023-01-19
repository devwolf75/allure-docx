import os
import sys
import click
from allure_docx.report_builder import ReportBuilder
from allure_docx.config import ReportConfig


def get_config_option_paths() -> {str: str}:
    """
    Returns a dictionary of the config option names with their corresponding path.
    """
    script_path = os.path.dirname(os.path.realpath(__file__))
    config_option_paths = {
        "standard": script_path + "/config/standard.ini",
        "standard_on_fail": script_path + "/config/standard_on_fail.ini",
        "compact": script_path + "/config/compact.ini",
        "no_trace": script_path + "/config/no_trace.ini"
    }
    return config_option_paths

@click.command()
@click.argument("allure_dir")
@click.argument("output")
@click.option(
    "--template",
    default=None,
    help="Path (absolute or relative) to a custom docx template file with styles",
)
@click.option(
    "--config",
    default="standard",
    help="Configuration for the docx report. Options are: standard, standard_on_fail, no_trace, compact. "
         "Alternatively path to custom .ini configuration file (see documentation).",
)
@click.option(
    "--pdf",
    is_flag=True,
    help="Try to generate a pdf file from created docx using soffice or OfficeToPDF (needs MS Word installed)",
)
@click.option("--title", default=None, help="Custom report title")
@click.option("--logo", default=None, help="Path to custom report logo image")
@click.option(
    "--logo-width",
    default=None,
    help="Image width in centimeters. Width is scaled to keep aspect ratio",
)
def main(allure_dir, output, template, pdf, title, logo, logo_width, config):
    """allure_dir: Path (relative or absolute) to allure_dir folder with test results

    output: Path (relative or absolute) with filename for the generated docx file"""

    def build_config():
        """
        builds the config by creating a ReportConfig object and adding additional configuration variables.
        """
        _config = ReportConfig()
        config_path = config
        config_option_paths = get_config_option_paths()
        if config in config_option_paths:
            config_path = config_option_paths[config]
        _config.read_config_from_file(config_path)

        if logo:
            _config['logo'] = {}
            _config['logo']['path'] = logo
            if logo_width:
                _config['logo']['width'] = logo_width
        if template:
            _config['template_path'] = template
        if 'title' not in _config['cover']:
            _config['cover']['title'] = title
        return _config

    cwd = os.getcwd()

    if not os.path.isabs(allure_dir):
        allure_dir = os.path.join(cwd, allure_dir)
    if not os.path.isabs(output):
        output = os.path.join(cwd, output)
    elif template and not os.path.isabs(template):
        template = os.path.join(cwd, template)
    print(f"Template: {template}")

    if logo_width is not None:
        logo_width = float(logo_width)

    report_config = build_config()
    report_builder = ReportBuilder(allure_dir=allure_dir, config=report_config)
    report_builder.save_report(output)

    if pdf:
        pdf_name, ext = os.path.splitext(output)
        pdf_name += ".pdf"
        report_builder.save_report_to_pdf(pdf_name)


if __name__ == "__main__":
    main()
