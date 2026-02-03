import re
import pandas as pd
from dataclasses import dataclass


@dataclass(frozen=True)
class DataCleanerConfig:
    """
    Config for data cleaning behavior.
    """
    drop_punct: bool = True
    collapse_whitespace: bool = True
    uppercase: bool = True
    keep_spaces: bool = True


class DataCleaner:
    """
    Utility class for cleaning text, identifiers, numbers, and dates.
    """

    _space_re = re.compile(r"\s+")
    _punct_re = re.compile(r"[^0-9A-Z ]+")
    _isin_re = re.compile(r"^[A-Z0-9]{12}$")

    def __init__(self, config: DataCleanerConfig = DataCleanerConfig()):
        """
        Create data cleaner with the given configuration.
        """
        self.config = config


    # ---- text
    def text(self, x):
        """
        Clean free-form text (names, labels).

        Returns cleaned string or None.
        """
        if pd.isna(x):
            return None
        s = str(x).strip()

        if self.config.uppercase:
            s = s.upper()

        if self.config.collapse_whitespace:
            s = self._space_re.sub(" ", s)

        if self.config.drop_punct:
            s = self._punct_re.sub(" ", s)
            s = self._space_re.sub(" ", s).strip()

        if not self.config.keep_spaces:
            s = s.replace(" ", "")

        return s or None
    
    # ---- ISIN
    # ISIN cleaner is not used in this project
    def isin(self, x, *, strict: bool = False):
        """
        Clean and validate an ISIN.

        returns 12-char ISIN or None.
        """
        if pd.isna(x):
            return None

        s = str(x).strip().upper()
        s = s.replace(" ", "")

        if not self._isin_re.match(s):
            if strict:
                raise ValueError(f"Invalid ISIN after cleaning: {x}")
            return None

        return s

    # ---- numbers
    def number(self, x):
        """
        clean numeric values to float.

        handle currency symbols, commas, percentages, and negatives.
        """
        if pd.isna(x):
            return None
        if isinstance(x, (int, float)) and not pd.isna(x):
            return float(x)

        s = str(x).strip()
        if s == "":
            return None

        neg = s.startswith("(") and s.endswith(")")
        s = s.strip("()")

        s = re.sub(r"[$£€,_ ]", "", s)

        is_pct = s.endswith("%")
        s = s[:-1] if is_pct else s

        try:
            val = float(s)
        except ValueError:
            return None

        if neg:
            val = -val
        if is_pct:
            val = val / 100.0

        return val

    #--- transaction number
    def trans_num(self, x):
        """
        Clean transaction number values and return non-negative integers only.
        Returns pd.NA if value cannot be safely converted.
        """
        if pd.isna(x):
            return pd.NA

        # Fast-path numeric types
        if isinstance(x, (int, float)):
            if float(x).is_integer() and x >= 0:
                return int(x)
            return pd.NA

        s = str(x).strip()
        if not s or s.startswith(("-", "(")):
            return pd.NA

        # Remove symbols and separators
        s = re.sub(r"[$£€,_ ]", "", s)

        try:
            val = float(s)
        except ValueError:
            return pd.NA

        return int(val) if val.is_integer() and val >= 0 else pd.NA


    # ---- dates
    def date(self, x):
        """
        clean date-like values to pandas timestamp.
        """
        if pd.isna(x) or str(x).strip() == "":
            return pd.NaT
        return pd.to_datetime(x, errors="coerce", infer_datetime_format=True)

    # --- pandas series helpers
    def apply_text(self, series: pd.Series) -> pd.Series:
        """
        apply text cleaning to pandas series.
        """
        return series.apply(self.text).astype("string")

    def apply_isin(self, series: pd.Series, *, strict: bool = False) -> pd.Series:
        """
        apply ISIN cleaning to pandas series
        """
        return series.apply(lambda x: self.isin(x, strict=strict)).astype("Int64")

    def apply_number(self, series: pd.Series) -> pd.Series:
        """
        apply numeric cleaning to pandas series
        """
        return series.apply(self.number).astype("float")

    def apply_date(self, series: pd.Series) -> pd.Series:
        """
        apply date cleaning to pandas series
        """
        return series.apply(self.date).astype("datetime64[ns]")
    
    def apply_trans_num(self, series: pd.Series) -> pd.Series:
        """
        apply transaction number cleaning to pandas series.
        """
        return series.apply(self.trans_num).astype("Int64")

