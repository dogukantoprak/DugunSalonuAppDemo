import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import type { Reservation } from "../api/client";

const COLUMN_HEADERS: Record<string, string> = {
    id: "ID",
    event_date: "Etkinlik Tarihi",
    start_time: "Başlangıç",
    end_time: "Bitiş",
    event_type: "Etkinlik Türü",
    guests: "Davetli",
    salon: "Salon",
    client_name: "Ad Soyad",
    bride_name: "Gelin",
    groom_name: "Damat",
    phone: "Telefon",
    status: "Durum",
    event_price: "Etkinlik Ücreti",
    menu_price: "Menü Ücreti",
    deposit_amount: "Kapora",
    payment_type: "Ödeme Türü",
    menu_name: "Menü",
    note: "Not",
};

const EXPORT_COLUMNS = [
    "id",
    "event_date",
    "start_time",
    "end_time",
    "event_type",
    "guests",
    "salon",
    "client_name",
    "bride_name",
    "groom_name",
    "phone",
    "status",
    "event_price",
    "menu_price",
    "deposit_amount",
    "payment_type",
    "menu_name",
    "note",
];

function formatDate(dateStr: string): string {
    if (!dateStr) return "";
    const [year, month, day] = dateStr.split("-");
    return `${day}/${month}/${year}`;
}

function prepareDataForExport(reservations: Reservation[]): Record<string, unknown>[] {
    return reservations.map((res) => {
        const row: Record<string, unknown> = {};
        EXPORT_COLUMNS.forEach((col) => {
            let value = res[col as keyof Reservation];
            if (col === "event_date" && typeof value === "string") {
                value = formatDate(value);
            }
            row[COLUMN_HEADERS[col] || col] = value ?? "";
        });
        return row;
    });
}

export function exportToExcel(reservations: Reservation[], filename = "rezervasyonlar"): void {
    const data = prepareDataForExport(reservations);
    const worksheet = XLSX.utils.json_to_sheet(data);

    // Set column widths
    const colWidths = EXPORT_COLUMNS.map((col) => ({
        wch: Math.max(COLUMN_HEADERS[col]?.length || 10, 12),
    }));
    worksheet["!cols"] = colWidths;

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Rezervasyonlar");

    const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
    const blob = new Blob([excelBuffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });

    const dateStr = new Date().toISOString().slice(0, 10);
    saveAs(blob, `${filename}_${dateStr}.xlsx`);
}
