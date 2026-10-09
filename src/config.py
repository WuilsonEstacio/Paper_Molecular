from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]  # raiz del proyecto
DOC_DIR = BASE_DIR / "Documentacion"
ARTICLES_DIR = BASE_DIR / "Articulos_libros"
LOG_DIR = BASE_DIR / "logs"
SRC_DIR = BASE_DIR / "src"

THEME_DIRS = {
    "01_Apoptosis_Anastasis": ARTICLES_DIR / "01_Apoptosis_Anastasis",
    "02_Mitocondria": ARTICLES_DIR / "02_Mitocondria",
    "03_DNA_Repair": ARTICLES_DIR / "03_DNA_Repair",
    "04_Membrane_Repair": ARTICLES_DIR / "04_Membrane_Repair",
    "05_ROS_Oxidative_Stress": ARTICLES_DIR / "05_ROS_Oxidative_Stress",
    "06_Autophagy_Mitophagy": ARTICLES_DIR / "06_Autophagy_Mitophagy",
    "07_Reprogramming_Rejuvenation": ARTICLES_DIR / "07_Reprogramming_Rejuvenation",
    "08_Senescence": ARTICLES_DIR / "08_Senescence",
    "09_Necroptosis_Ferroptosis_Pyroptosis": ARTICLES_DIR / "09_Necroptosis_Ferroptosis_Pyroptosis",
    "10_Computational_Modeling": ARTICLES_DIR / "10_Computational_Modeling",
    "11_Cell_Regeneration": ARTICLES_DIR / "11_Cell_Regeneration",
    "12_Reviews": ARTICLES_DIR / "12_Reviews",
    "13_Theses_Books": ARTICLES_DIR / "13_Theses_Books",
    "99_Other": ARTICLES_DIR / "99_Other",
}

CATALOG_XLSX = ARTICLES_DIR / "catalogo_articulos.xlsx"
CATALOG_CSV = ARTICLES_DIR / "catalogo_articulos.csv"
TOP50_XLSX = ARTICLES_DIR / "top_50_articulos_clave.xlsx"
README_MD = ARTICLES_DIR / "README_BIBLIOGRAFIA.md"
