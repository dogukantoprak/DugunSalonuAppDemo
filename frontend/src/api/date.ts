function pad(value: number | string): string {
  return String(value).padStart(2, "0");
}

const ISO_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

function buildDisplayDate(day: string | number, month: string | number, year: string | number): string {
  return `${pad(day)}/${pad(month)}/${year}`;
}

export function normalizeToIsoDate(input: string | Date | null | undefined): string {
  if (!input) return "";
  if (input instanceof Date && !Number.isNaN(input.getTime())) {
    return input.toISOString().slice(0, 10);
  }

  const text = String(input).trim();
  if (!text) return "";

  const isoLike = text.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})/);
  if (isoLike) {
    const [, year, month, day] = isoLike;
    return `${year}-${pad(month)}-${pad(day)}`;
  }

  const dmy = text.match(/^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$/);
  if (dmy) {
    const [, day, month, year] = dmy;
    return `${year}-${pad(month)}-${pad(day)}`;
  }

  const parsed = new Date(text);
  if (!Number.isNaN(parsed.getTime())) {
    return parsed.toISOString().slice(0, 10);
  }

  return text;
}

export function formatDisplayDate(value: string | Date | null | undefined): string {
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

  return String(value);
}

export function isIsoDate(value: unknown): boolean {
  if (typeof value !== "string" || !ISO_DATE_PATTERN.test(value)) {
    return false;
  }
  const [year, month, day] = value.split("-").map(Number);
  const utcDate = new Date(Date.UTC(year, month - 1, day));
  return (
    utcDate.getUTCFullYear() === year &&
    utcDate.getUTCMonth() + 1 === month &&
    utcDate.getUTCDate() === day
  );
}

export function formatInputDate(value: string | Date | null | undefined): string {
  if (!value) return "";
  const formatted = formatDisplayDate(value);
  return formatted === "—" ? "" : formatted;
}
