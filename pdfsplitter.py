from PyPDF2 import PdfFileWriter, PdfFileReader

inputpdf = PdfFileReader(open("b:/temp/all.pdf", "rb"))

for i in range(inputpdf.numPages):
    output = PdfFileWriter()
    output.addPage(inputpdf.getPage(i))
    with open("b:/temp/document-page20%s.pdf" % i, "wb") as outputStream:
        output.write(outputStream)