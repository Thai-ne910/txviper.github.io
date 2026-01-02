@startuml Food Ordering System Sequence Diagram

actor Customer
participant "Web Frontend" as Frontend
participant "API Gateway" as Gateway
participant "Auth Service" as Auth
participant "Order Service" as Order
participant "Payment Service" as Payment
participant "Notification Service" as Notify
database "Database" as DB

== Authentication Flow ==
Customer -> Frontend: Access system
Frontend -> Gateway: Request login
Gateway -> Auth: Authenticate user
Auth -> DB: Verify credentials
Auth --> Gateway: Return JWT token
Gateway --> Frontend: Return token
Frontend --> Customer: Show dashboard

== Order Placement Flow ==
Customer -> Frontend: Place order
Frontend -> Gateway: Submit order
Gateway -> Order: Create order
Order -> DB: Save order
Order -> Payment: Process payment
Payment -> DB: Update payment status
Payment --> Order: Payment confirmation
Order -> Notify: Send order confirmation
Notify --> Customer: Email/SMS notification
Order --> Gateway: Order confirmation
Gateway --> Frontend: Update UI
Frontend --> Customer: Show confirmation

== Order Management Flow ==
Customer -> Frontend: View orders
Frontend -> Gateway: Request orders
Gateway -> Order: Get orders
Order -> DB: Query orders
DB --> Order: Return orders
Order --> Gateway: Return order data
Gateway --> Frontend: Display orders
Frontend --> Customer: Show order list

== Payment Processing Flow ==
Customer -> Frontend: Make payment
Frontend -> Gateway: Submit payment
Gateway -> Payment: Process payment
Payment -> DB: Update payment status
Payment -> Notify: Send payment confirmation
Notify --> Customer: Payment confirmation
Payment --> Gateway: Payment result
Gateway --> Frontend: Update UI
Frontend --> Customer: Show payment status

@enduml 