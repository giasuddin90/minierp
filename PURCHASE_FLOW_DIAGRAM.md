# Purchase Flow Diagram

## 📊 **Purchase Flow Visualization**

```
┌─────────────────────────────────────────────────────────────────┐
│                        PURCHASE FLOW                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CREATE PO     │    │  RECEIVE GOODS  │    │   CANCEL PO     │
│                 │    │                 │    │                 │
│ Status:         │    │ Status:         │    │ Status:         │
│ purchase-order  │    │ goods-received   │    │ canceled        │
│                 │    │                 │    │                 │
│ • Order Number  │    │ • Update Stock  │    │ • No Stock      │
│ • Supplier      │    │ • Invoice ID    │    │   Updates       │
│ • Items         │    │ • Receipt Date  │    │ • Order Closed  │
│ • Expected Date │    │ • Notes         │    │ • No Further    │
│ • Total Amount  │    │                 │    │   Actions       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PO DETAILS    │    │  GOODS RECEIPT  │    │  CANCELED PO    │
│                 │    │                 │    │                 │
│ • View Items    │    │ • Invoice ID    │    │ • View Details  │
│ • Edit Order    │    │ • Receipt Date  │    │ • No Actions    │
│ • Receive Goods │    │ • Update Stock  │    │ • Closed        │
│ • Cancel Order  │    │ • Create GR     │    │                 │
│ • Create GR     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔄 **Status Transitions**

```
┌─────────────────┐
│ purchase-order  │ ──────────────────────────────────┐
│                 │                                   │
│ • Initial State│                                   │
│ • Can Edit     │                                   │
│ • Can Receive  │                                   │
│ • Can Cancel   │                                   │
└─────────────────┘                                   │
         │                                             │
         │ Receive Goods                               │ Cancel Order
         │                                             │
         ▼                                             ▼
┌─────────────────┐                           ┌─────────────────┐
│ goods-received  │                           │   canceled      │
│                 │                           │                 │
│ • Final State   │                           │ • Final State   │
│ • Stock Updated │                           │ • No Changes    │
│ • Can Create GR │                           │ • Closed        │
│ • No Further    │                           │ • No Further    │
│   Actions       │                           │   Actions       │
└─────────────────┘                           └─────────────────┘
```

## 📋 **Purchase Order Lifecycle**

```
1. CREATE PURCHASE ORDER
   ├── Status: purchase-order
   ├── Order Number: PO-001
   ├── Supplier: ABC Company
   ├── Items: Product A (10 units), Product B (5 units)
   ├── Expected Date: 2024-01-15
   └── Total Amount: $1,500.00

2. RECEIVE GOODS (Option A)
   ├── Status: goods-received
   ├── Stock Updated: +10 Product A, +5 Product B
   ├── Invoice ID: SUP-INV-12345
   ├── Receipt Date: 2024-01-14
   └── Goods Receipt: GR-001

3. CANCEL ORDER (Option B)
   ├── Status: canceled
   ├── No Stock Updates
   ├── Order Closed
   └── No Further Actions
```

## 🎯 **User Actions by Status**

### **Purchase Order Status**
```
┌─────────────────────────────────────────────────────────────────┐
│                    PURCHASE ORDER STATUS                       │
├─────────────────────────────────────────────────────────────────┤
│ Actions Available:                                             │
│ • View Details                                                 │
│ • Edit Order                                                 │
│ • Receive Goods                                               │
│ • Cancel Order                                                │
│ • Create Goods Receipt                                        │
└─────────────────────────────────────────────────────────────────┘
```

### **Goods Received Status**
```
┌─────────────────────────────────────────────────────────────────┐
│                   GOODS RECEIVED STATUS                        │
├─────────────────────────────────────────────────────────────────┤
│ Actions Available:                                             │
│ • View Details                                                 │
│ • Create Goods Receipt                                         │
│ • View Stock Updates                                           │
│ • No Further Status Changes                                    │
└─────────────────────────────────────────────────────────────────┘
```

### **Canceled Status**
```
┌─────────────────────────────────────────────────────────────────┐
│                     CANCELED STATUS                            │
├─────────────────────────────────────────────────────────────────┤
│ Actions Available:                                             │
│ • View Details                                                 │
│ • No Further Actions                                           │
│ • Order Closed                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 **Database Schema**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PURCHASE ORDER TABLE                        │
├─────────────────────────────────────────────────────────────────┤
│ id              │ Primary Key                                 │
│ order_number    │ Unique Order Number (PO-001)                 │
│ supplier        │ Foreign Key to Supplier                      │
│ order_date      │ Date Order Created                           │
│ expected_date   │ Expected Delivery Date                       │
│ status          │ purchase-order | goods-received | canceled  │
│ total_amount    │ Total Order Amount                           │
│ notes           │ Additional Notes                             │
│ created_by      │ User Who Created Order                       │
│ created_at      │ Creation Timestamp                           │
│ updated_at      │ Last Update Timestamp                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    GOODS RECEIPT TABLE                         │
├─────────────────────────────────────────────────────────────────┤
│ id              │ Primary Key                                 │
│ receipt_number  │ Unique Receipt Number (GR-001)              │
│ purchase_order  │ Foreign Key to Purchase Order                │
│ receipt_date    │ Date Goods Received                          │
│ invoice_id      │ Invoice ID from Supplier                     │
│ status          │ draft | received | cancelled                │
│ total_amount    │ Total Receipt Amount                         │
│ notes           │ Additional Notes                             │
│ created_by      │ User Who Created Receipt                     │
│ created_at      │ Creation Timestamp                           │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 **Implementation Flow**

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION STEPS                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Create Purchase Order                                       │
│    ├── Set status = 'purchase-order'                           │
│    ├── Add items to order                                      │
│    └── Calculate total amount                                  │
│                                                                 │
│ 2. Receive Goods                                                │
│    ├── Change status to 'goods-received'                       │
│    ├── Update stock levels                                     │
│    ├── Create stock movements                                  │
│    └── Allow goods receipt creation                            │
│                                                                 │
│ 3. Cancel Order                                                 │
│    ├── Change status to 'canceled'                             │
│    ├── No stock updates                                        │
│    └── Close order                                             │
│                                                                 │
│ 4. Create Goods Receipt (Optional)                             │
│    ├── Link to purchase order                                  │
│    ├── Add invoice ID                                          │
│    ├── Set receipt date                                        │
│    └── Add notes                                               │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 **UI/UX Design**

```
┌─────────────────────────────────────────────────────────────────┐
│                    PURCHASE ORDER LIST                         │
├─────────────────────────────────────────────────────────────────┤
│ Order #    │ Supplier    │ Status        │ Actions             │
│ PO-001     │ ABC Co      │ 🟡 Pending    │ View │ Receive │ Cancel │
│ PO-002     │ XYZ Ltd     │ 🟢 Received   │ View │ Details │        │
│ PO-003     │ DEF Inc     │ 🔴 Canceled   │ View │ Details │        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    PURCHASE ORDER DETAIL                       │
├─────────────────────────────────────────────────────────────────┤
│ Order Information:                                             │
│ • Order Number: PO-001                                         │
│ • Supplier: ABC Company                                        │
│ • Status: 🟡 Purchase Order                                   │
│ • Order Date: 2024-01-10                                       │
│ • Expected Date: 2024-01-15                                    │
│ • Total Amount: $1,500.00                                    │
│                                                                 │
│ Items:                                                         │
│ • Product A: 10 units @ $100.00 = $1,000.00                   │
│ • Product B: 5 units @ $100.00 = $500.00                      │
│                                                                 │
│ Actions:                                                       │
│ • [Receive Goods] [Cancel Order] [Create Goods Receipt]       │
└─────────────────────────────────────────────────────────────────┘
```

This purchase flow provides a clear, simple, and business-friendly approach to managing purchase orders with proper status tracking and stock management! 🎉
