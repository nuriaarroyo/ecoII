import re
from pathlib import Path
from urllib.parse import quote
import plotly.io as pio


class PlotlyPagesPublisher:
    """
    Save Plotly figures as HTML into a GitHub Pages folder and generate:
    - browser URL (human readable)
    - PDF-safe URL (ASCII-only, percent-encoded) that survives PDF export
    """

    def __init__(
        self,
        github_username: str,
        github_repo: str,
        pages_root: str = "docs",
        repo_root: Path | None = None,
    ):
        self.github_username = github_username
        self.github_repo = github_repo
        self.pages_root = pages_root
        self.repo_root = repo_root or self.find_repo_root(Path.cwd())

    # ---------- helpers ----------
    @staticmethod
    def slugify(text: str) -> str:
        text = (text or "").strip()
        text = re.sub(r"[^\w\d\-]+", "_", text, flags=re.UNICODE)
        text = re.sub(r"_+", "_", text).strip("_")
        return text or "plotly_figure"

    @staticmethod
    def find_repo_root(start: Path | None = None) -> Path:
        start = start or Path.cwd()
        for p in [start, *start.parents]:
            if (p / ".git").exists() or (p / "README.md").exists():
                return p
        return start

    @staticmethod
    def pdf_safe_url(public_url: str) -> str:
        """
        Percent-encode non-ASCII characters so PDF exporters don't drop/break the link.
        """
        if not public_url:
            return ""
        return quote(public_url, safe=":/#?&=%")

    # ---------- main API ----------
    def save_html(
        self,
        fig,
        site_subfolder: str = "interactive",
        filename: str | None = None,
        auto_open: bool = False,
        print_link: bool = False,
        return_pdf_safe: bool = True,
    ):
        """
        Saves the Plotly figure as HTML under:
          <repo_root>/<pages_root>/<site_subfolder>/<filename>

        If filename is None, it is derived from fig.layout.title.text.

        Returns:
          (out_path, public_url, pdf_url)  if return_pdf_safe=True
          (out_path, public_url)           otherwise
        """
        # 1) filename
        if filename is None:
            title = getattr(fig.layout.title, "text", None) or "plotly_figure"
            filename = self.slugify(title) + ".html"
        else:
            filename = filename if filename.endswith(".html") else (filename + ".html")

        # 2) output directory
        out_dir = self.repo_root / self.pages_root / site_subfolder
        out_dir.mkdir(parents=True, exist_ok=True)

        # 3) save path
        out_path = out_dir / filename

        # 4) write HTML
        pio.write_html(
            fig,
            file=str(out_path),
            full_html=True,
            include_plotlyjs="cdn",
            auto_open=auto_open,
        )

        # 5) public URL
        public_url = (
            f"https://{self.github_username}.github.io/"
            f"{self.github_repo}/{site_subfolder}/{filename}"
        )

        pdf_url = self.pdf_safe_url(public_url)

        if print_link:
            print("✅ Interactive Plotly URL:")
            print(public_url)
            print("✅ PDF-safe URL:")
            print(pdf_url)

        if return_pdf_safe:
            return out_path, public_url, pdf_url
        return out_path, public_url
