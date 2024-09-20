from fpdf import FPDF

def generate_invoice(booking):
    # Create instance of FPDF class
    pdf = FPDF()

    # Add page
    pdf.add_page()

    # Set font and size for header
    pdf.set_font('Arial', 'B', 16)

    # Write header
    pdf.cell(0, 10, 'Booking Receipt', 0, 1, 'C')

    # Set font and size for sub-header
    pdf.set_font('Arial', 'B', 12)

    # Write sub-header
    pdf.cell(50, 10, 'Booking ID:', 0, 0, 'L')
    pdf.cell(0, 10, str(booking.id), 0, 1, 'L')

    pdf.cell(50, 10, 'Booking Time:', 0, 0, 'L')
    pdf.cell(0, 10, booking.booking_time.strftime('%d/%m/%Y %H:%M:%S'), 0, 1, 'L')

    pdf.cell(50, 10, 'Departure Time:', 0, 0, 'L')
    pdf.cell(0, 10, booking.journey.departure_time.strftime('%d/%m/%Y %H:%M:%S'), 0, 1, 'L')

    pdf.cell(50, 10, 'Arrival Time:', 0, 0, 'L')
    pdf.cell(0, 10, booking.journey.arrival_time.strftime('%d/%m/%Y %H:%M:%S'), 0, 1, 'L')

    pdf.cell(50, 10, 'Departure:', 0, 0, 'L')
    pdf.cell(0, 10, booking.journey.departure, 0, 1, 'L')

    pdf.cell(50, 10, 'Destination:', 0, 0, 'L')
    pdf.cell(0, 10, booking.journey.destination, 0, 1, 'L')

    pdf.cell(50, 10, 'Travel Option:', 0, 0, 'L')
    pdf.cell(0, 10, booking.journey.travel_option, 0, 1, 'L')

    pdf.cell(50, 10, 'Seats Booked:', 0, 0, 'L')
    pdf.cell(0, 10, str(booking.seats_booked), 0, 1, 'L')

    pdf.cell(50, 10, 'Amount Paid:', 0, 0, 'L')
    pdf.cell(0, 10, str(booking.amount_paid), 0, 1, 'L')

    # Save the PDF
    return pdf