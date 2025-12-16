function pad(value) {
  return String(value).padStart(2, "0");
}

function buildDisplayDate(day, month, year) {
  return `${pad(day)}/${pad(month)}/${year}`;
}

export function normalizeToIsoDate(input) {
  if (!input) return "";
  if (input instanceof Date && !Number.isNaN(input.getTime())) {
    return input.toISOString().slice(0, 10);
  }

  const text = String(input).trim();
  if (!text) return "";

  const isoLike = text.match(/^(\d{4})[-/.](\d{2})[-/.](\d{2})/);
  if (isoLike) {
    const [, year, month, day] = isoLike;
    return `${year}-${month}-${day}`;
  }

  const dmy = text.match(/^(\d{2})[-/.](\d{2})[-/.](\d{4})$/);
  if (dmy) {
    const [, day, month, year] = dmy;
    return `${year}-${month}-${day}`;
  }

  const parsed = new Date(text);
  if (!Number.isNaN(parsed.getTime())) {
    return parsed.toISOString().slice(0, 10);
  }

  return text;
}

export function formatDisplayDate(value) {
  if (!value) return "—";

  if (value instanceof Date && !Number.isNaN(value.getTime())) {
    return buildDisplayDate(value.getDate(), value.getMonth() + 1, value.getFullYear());
  }

  if (typeof value === "string") {
    const isoMatch = value.match(/^(\d{4})[-/.](\d{2})[-/.](\d{2})/);
    if (isoMatch) {
      const [, year, month, day] = isoMatch;
      return buildDisplayDate(day, month, year);
    }

    const dmyMatch = value.match(/^(\d{2})[-/.](\d{2})[-/.](\d{4})$/);
    if (dmyMatch) {
      const [, day, month, year] = dmyMatch;
      return buildDisplayDate(day, month, year);
    }

    const mdyMatch = value.match(/^(\d{2})[-/](\d{2})[-/](\d{4})$/);
    if (mdyMatch) {
      const [, month, day, year] = mdyMatch;
      return buildDisplayDate(day, month, year);
    }
  }

  const parsed = new Date(value);
  if (!Number.isNaN(parsed.getTime())) {
    return new Intl.DateTimeFormat("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(parsed);
  }

  return value;
}
