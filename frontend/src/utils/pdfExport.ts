import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import type { Reservation } from "../api/client";

function formatDate(dateStr: string): string {
    if (!dateStr) return "";
    const [year, month, day] = dateStr.split("-");
    return `${day}/${month}/${year}`;
}

function formatCurrency(value: number | undefined): string {
    if (value === undefined || value === null) return "-";
    return new Intl.NumberFormat("tr-TR", {
        style: "currency",
        currency: "TRY",
    }).format(value);
}

export function generateContractPDF(reservation: Reservation): void {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();

    // Header
    doc.setFontSize(20);
    doc.setFont("helvetica", "bold");
    doc.text("DUGUN SALONU REZARVASYON SOZLESMESI", pageWidth / 2, 25, { align: "center" });

    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.text(`Sozlesme No: ${reservation.contract_no || "-"}`, 20, 40);
    doc.text(`Tarih: ${formatDate(reservation.contract_date || reservation.event_date)}`, pageWidth - 20, 40, { align: "right" });

    // Divider
    doc.setDrawColor(100);
    doc.line(20, 45, pageWidth - 20, 45);

    // Event Details Table
    const eventDetails = [
        ["Etkinlik Tarihi", formatDate(reservation.event_date)],
        ["Saat", `${reservation.start_time} - ${reservation.end_time}`],
        ["Etkinlik Turu", reservation.event_type || "-"],
        ["Salon", reservation.salon || "-"],
        ["Davetli Sayisi", String(reservation.guests || "-")],
        ["Durum", reservation.status || "-"],
    ];

    autoTable(doc, {
        startY: 55,
        head: [["ETKINLIK BILGILERI", ""]],
        body: eventDetails,
        theme: "striped",
        headStyles: { fillColor: [59, 130, 246], textColor: 255 },
        styles: { fontSize: 10 },
        columnStyles: { 0: { fontStyle: "bold", cellWidth: 60 } },
    });

    // Client Details Table  
    const clientDetails = [
        ["Ad Soyad", reservation.client_name || "-"],
        ["Gelin", reservation.bride_name || "-"],
        ["Damat", reservation.groom_name || "-"],
        ["TC Kimlik", reservation.tc_identity || "-"],
        ["Telefon", reservation.phone || "-"],
        ["Adres", reservation.address || "-"],
        ["Memleket", reservation.region || "-"],
    ];

    const finalY1 = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY || 90;

    autoTable(doc, {
        startY: finalY1 + 10,
        head: [["MUSTERI BILGILERI", ""]],
        body: clientDetails,
        theme: "striped",
        headStyles: { fillColor: [16, 185, 129], textColor: 255 },
        styles: { fontSize: 10 },
        columnStyles: { 0: { fontStyle: "bold", cellWidth: 60 } },
    });

    // Payment Details Table
    const paymentDetails = [
        ["Kisi Basi Etkinlik Ucreti", formatCurrency(reservation.event_price)],
        ["Kisi Basi Menu Ucreti", formatCurrency(reservation.menu_price)],
        ["Kapora Yuzdesi", reservation.deposit_percent ? `%${reservation.deposit_percent}` : "-"],
        ["Kapora Tutari", formatCurrency(reservation.deposit_amount)],
        ["Taksit Sayisi", String(reservation.installments || "-")],
        ["Odeme Turu", reservation.payment_type || "-"],
    ];

    const finalY2 = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY || 140;

    autoTable(doc, {
        startY: finalY2 + 10,
        head: [["ODEME BILGILERI", ""]],
        body: paymentDetails,
        theme: "striped",
        headStyles: { fillColor: [139, 92, 246], textColor: 255 },
        styles: { fontSize: 10 },
        columnStyles: { 0: { fontStyle: "bold", cellWidth: 60 } },
    });

    // Menu Info
    if (reservation.menu_name || reservation.menu_detail) {
        const finalY3 = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY || 180;

        autoTable(doc, {
            startY: finalY3 + 10,
            head: [["MENU BILGILERI", ""]],
            body: [
                ["Menu", reservation.menu_name || "-"],
                ["Detay", reservation.menu_detail || "-"],
                ["Ozel Istekler", reservation.special_request || "-"],
            ],
            theme: "striped",
            headStyles: { fillColor: [245, 158, 11], textColor: 255 },
            styles: { fontSize: 10 },
            columnStyles: { 0: { fontStyle: "bold", cellWidth: 60 } },
        });
    }

    // Footer with signature lines
    const finalY4 = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY || 220;

    if (finalY4 < 250) {
        doc.setFontSize(10);
        doc.text("Salon Yetkilisi", 40, finalY4 + 30);
        doc.text("Musteri", pageWidth - 60, finalY4 + 30);

        doc.line(20, finalY4 + 40, 80, finalY4 + 40);
        doc.line(pageWidth - 80, finalY4 + 40, pageWidth - 20, finalY4 + 40);
    }

    // Save
    const dateStr = reservation.event_date || new Date().toISOString().slice(0, 10);
    const clientName = (reservation.client_name || "musteri").replace(/\s+/g, "_");
    doc.save(`sozlesme_${clientName}_${dateStr}.pdf`);
}
