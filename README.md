# Building Materials ERP System

A comprehensive Django-based ERP system for building materials business management, built according to the PRD specifications.

## 🚀 Features Implemented

### Core Modules

#### 1. **Bank Management**
- Multiple bank accounts support
- Bank transactions (deposits, withdrawals, transfers)
- Loan management with deal numbers
- Loan transaction tracking
- Bank account statements
- Trial balance generation

#### 2. **Customer Management**
- Retail and Wholesale customer support
- Customer ledger with transaction tracking
- Commission management (per transaction/party)
- Customer commitments with SMS reminders
- Credit limit management

#### 3. **Supplier Management**
- Supplier database with contact information
- Supplier ledger for purchase tracking
- Commission management
- Terms and conditions tracking

#### 4. **Inventory Management**
- Warehouse/godown management
- Product categories (Cement, Rod, Tiles, Paint, Others)
- Multiple unit types (bags, bundles, pieces, kg, sqft, liters)
- Real-time stock tracking
- Stock movements (inward/outward)
- Low stock alerts
- Stock valuation

#### 5. **Sales Management**
- Sales Order (SO) → Delivery → Sales Invoice workflow
- Cash and Credit sales
- Auto SMS notifications
- Auto labor charges for retail sales
- Customer ledger integration
- Sales returns and payments

#### 6. **Purchase Management**
- Purchase Order (PO) → Goods Receipt → Purchase Invoice workflow
- Supplier ledger integration
- Purchase returns and payments
- Stock auto-update on receipt

#### 7. **Reporting System**
- Daily reports (sales, collections, bank deposits)
- Monthly reports (customer/supplier summaries)
- Trial balance with cash accounting
- Bank reports and loan tracking
- Stock reports and valuation

## 🛠 Technical Implementation

### Django Architecture
- **Framework**: Django 5.0+
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: Bootstrap 5.3.2 with custom styling
- **Icons**: Bootstrap Icons
- **Charts**: Chart.js for reporting

### Project Structure
```
building_materials_full/
├── core/                   # Main Django settings
├── accounting/            # Bank, loans, trial balance
├── customers/            # Customer management
├── suppliers/            # Supplier management
├── stock/                # Inventory management
├── sales/                # Sales management
├── purchases/            # Purchase management
├── templates/            # HTML templates
├── static/               # Static files
└── logs/                 # Application logs
```

### Models Implemented

#### Accounting Models
- `BankAccount` - Bank account management
- `BankTransaction` - Bank transactions
- `Loan` - Loan management
- `LoanTransaction` - Loan payments
- `TrialBalance` - Daily trial balance

#### Customer Models
- `Customer` - Customer information
- `CustomerLedger` - Customer transaction ledger
- `CustomerCommission` - Commission rates
- `CustomerCommitment` - Payment commitments

#### Supplier Models
- `Supplier` - Supplier information
- `SupplierLedger` - Supplier transaction ledger
- `SupplierCommission` - Commission rates

#### Stock Models
- `Warehouse` - Warehouse locations
- `ProductCategory` - Product categories
- `Product` - Product information
- `Stock` - Current stock levels
- `StockMovement` - Stock movements
- `StockAlert` - Low stock alerts

#### Sales Models
- `SalesOrder` - Sales orders
- `SalesOrderItem` - Order line items
- `SalesInvoice` - Sales invoices
- `SalesInvoiceItem` - Invoice line items
- `SalesReturn` - Sales returns
- `SalesReturnItem` - Return line items
- `SalesPayment` - Sales payments

#### Purchase Models
- `PurchaseOrder` - Purchase orders
- `PurchaseOrderItem` - Order line items
- `GoodsReceipt` - Goods receipts
- `GoodsReceiptItem` - Receipt line items
- `PurchaseInvoice` - Purchase invoices
- `PurchaseInvoiceItem` - Invoice line items
- `PurchaseReturn` - Purchase returns
- `PurchaseReturnItem` - Return line items
- `PurchasePayment` - Purchase payments

## 🎨 User Interface

### Design Features
- **Modern Bootstrap 5.3.2** design with gradient styling
- **Responsive sidebar navigation** with icons
- **Card-based layouts** for better organization
- **Professional color scheme** with purple/blue gradients
- **Mobile-friendly** responsive design
- **Auto-hiding alerts** for better UX

### Navigation Structure
- Dashboard (Admin interface)
- Banking (Bank accounts, loans, transactions)
- Customers (Customer management, ledgers, commissions)
- Suppliers (Supplier management, ledgers)
- Inventory (Products, stock, warehouses)
- Sales (Orders, invoices, returns, payments)
- Purchases (Orders, receipts, invoices, returns)
- Reports (Daily, monthly, trial balance)

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd building_materials_full
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the system**
   - Open browser to `http://localhost:8000`
   - Login with superuser credentials
   - Access admin interface at `http://localhost:8000/admin`

## 📊 Admin Interface

The Django admin interface provides comprehensive management for all modules:

### Banking
- Bank accounts management
- Transaction recording
- Loan management
- Trial balance generation

### Customer Management
- Customer database
- Ledger entries
- Commission settings
- Commitment tracking

### Supplier Management
- Supplier database
- Ledger entries
- Commission settings

### Inventory
- Warehouse management
- Product categories
- Product catalog
- Stock levels
- Movement tracking

### Sales & Purchases
- Order management
- Invoice processing
- Return handling
- Payment tracking

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production settings:
```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
SMS_API_KEY=your-sms-api-key
SMS_API_URL=your-sms-api-url
```

### Database Configuration
- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

## 📈 Business Logic

### Workflow Implementation

#### Sales Workflow
1. Create Sales Order (SO)
2. Process delivery
3. Generate Sales Invoice
4. Auto SMS notification
5. Auto labor charges (retail only)
6. Update customer ledger
7. Update stock levels

#### Purchase Workflow
1. Create Purchase Order (PO)
2. Process goods receipt
3. Generate Purchase Invoice
4. Update supplier ledger
5. Update stock levels

#### Trial Balance Logic
- **Cash Inflows**: Sales, collections, withdrawals, loans
- **Cash Outflows**: Purchases, expenses, deposits, loan payments
- **Balancing**: Debit Side = Credit Side + Closing Balance
- **Discrepancy Detection**: Automatic flagging of mismatches

## 🔒 Security Features

- **Role-based access control**
- **CSRF protection**
- **XSS protection**
- **Secure headers**
- **Password validation**
- **Session management**

## 📱 Future Enhancements

### Planned Features
- **Mobile app** (React Native/Flutter)
- **Offline-first capability**
- **Advanced reporting** with charts
- **SMS automation** integration
- **Email notifications**
- **Barcode scanning**
- **Multi-language support**
- **Advanced analytics**

## 🐛 Troubleshooting

### Common Issues

1. **Migration errors**
   ```bash
   python manage.py makemigrations --empty app_name
   python manage.py migrate
   ```

2. **Static files not loading**
   ```bash
   python manage.py collectstatic
   ```

3. **Permission errors**
   ```bash
   chmod +x manage.py
   ```

## 📞 Support

For technical support or feature requests, please contact the development team.

## 📄 License

This project is proprietary software. All rights reserved.

---

**Built with ❤️ using Django and Bootstrap**
