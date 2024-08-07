from rest_framework import viewsets,status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
import csv
from django.http import HttpResponse
from datetime import datetime,timedelta
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

@api_view(['GET'])
def export_expenses(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Category', 'Amount', 'Description', 'Date'])

    expenses = Expense.objects.all().values_list('category__name', 'amount', 'description', 'date')
    total_amount = Expense.objects.aggregate(Sum('amount'))['amount__sum']

    for expense in expenses:
        writer.writerow(expense)

    writer.writerow(['Total', total_amount])

    return response

@ api_view(['GET'])
def oneWeek(request):
    aWeekAgo = datetime.now().date()-timedelta(days = 7)
    expenseOfWeek = Expense.objects.filter(date__gte = aWeekAgo)
    print(expenseOfWeek,111111, aWeekAgo)
    if not expenseOfWeek.exists():
        return Response({"message":"No available data in the last 7-days" }, status=404)
    serializer =ExpenseSerializer(expenseOfWeek,many =True)

    return Response(serializer.data)

@api_view(['GET'])
def last15Days(request):
    days = datetime.now().date() - timedelta(days=15)
    expenseOf15day = Expense.objects.filter(date__gte = days)
    if not expenseOf15day.exists():
        return Response({"message":"No available data in last 15-days "},status=404)
    serializer =ExpenseSerializer(expenseOf15day, many =True)

    return Response(serializer.data)

@api_view(["GET"])
def customDates(request):
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if not from_date or not to_date:
        return Response({"error":"Both *from_date* and *to_date* parameters are required."}, status= status.HTTP_400_BAD_REQUEST)
    expenses =Expense.objects.filter(date__range =[from_date,to_date])
    if not expenses.exists():
        return Response({"message":"No available data in the specified date range."}, status= status.HTTP_404_NOT_FOUND)
    serializer = ExpenseSerializer(expenses, many = True)

    return Response(serializer.data)

@api_view(['GET'])
def today(request):
    today = datetime.now().date()
    td_expenses = Expense.objects.filter(date = today)
    if not td_expenses.exists():
        return Response({"message":"Today No Data Available"})
    serializer = ExpenseSerializer(td_expenses, many = True)
    return Response(serializer.data)


@api_view(['GET'])
def export_expenses_pdf(request):

    buffer = BytesIO()
    

    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    p.setTitle('Expenses')
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, height - 40, "Expenses Report")
   
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, height - 100, "Category")
    p.drawString(200, height - 100, "Amount")
    p.drawString(300, height - 100, "Description")
    p.drawString(450, height - 100, "Date")


    expenses = Expense.objects.all().values_list('category__name', 'amount', 'description', 'date')
    p.setFont("Helvetica", 10)
    y = height - 120
    for expense in expenses:
        p.drawString(50, y, str(expense[0]))
        p.drawString(200, y, str(expense[1]))
        p.drawString(300, y, str(expense[2]))
        p.drawString(450, y, str(expense[3]))
        y -= 20

    # Total amount
    total_amount = Expense.objects.aggregate(Sum('amount'))['amount__sum']
    p.drawString(50, y - 20, "Total Amount")
    p.drawString(200, y - 20, str(total_amount))
    p.setFont("Helvetica", 8)
    footer_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    p.drawString(50, 30, footer_text)
  
    p.showPage()
    p.save()

    
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

