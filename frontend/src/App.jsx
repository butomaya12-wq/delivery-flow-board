import { useState } from 'react'
import './App.css'
import { createOrder, listOrders, ORDER_STATUSES, updateOrderStatus } from './api.js'

const EMPTY_FORM = {
  customer_name: '',
  delivery_address: '',
  order_summary: '',
}

const FIELD_LABELS = {
  customer_name: 'Customer name',
  delivery_address: 'Delivery address',
  order_summary: 'Order summary',
}

function App() {
  const [orders, setOrders] = useState(() => listOrders())
  const [formData, setFormData] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})

  function handleInputChange(event) {
    const { name, value } = event.target

    setFormData((currentData) => ({ ...currentData, [name]: value }))
    setErrors((currentErrors) => ({ ...currentErrors, [name]: '' }))
  }

  function handleCreateOrder(event) {
    event.preventDefault()

    const nextErrors = Object.fromEntries(
      Object.entries(formData)
        .filter(([, value]) => !value.trim())
        .map(([field]) => [field, `Enter ${FIELD_LABELS[field]}.`]),
    )

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors)
      return
    }

    createOrder(formData)
    setOrders(listOrders())
    setFormData(EMPTY_FORM)
    setErrors({})
  }

  function handleStatusChange(orderId, status) {
    updateOrderStatus(orderId, status)
    setOrders(listOrders())
  }

  return (
    <main className="app">
      <header className="page-header">
        <p className="eyebrow">Delivery Flow Board</p>
        <h1>Delivery order management</h1>
        <p>Create orders and track their progress through each delivery stage.</p>
      </header>

      <section className="create-order" aria-labelledby="create-order-title">
        <div>
          <p className="section-label">New order</p>
          <h2 id="create-order-title">Add an order</h2>
        </div>

        <form className="order-form" onSubmit={handleCreateOrder} noValidate>
          {Object.keys(EMPTY_FORM).map((field) => (
            <label className="field" key={field}>
              <span>{FIELD_LABELS[field]}</span>
              {field === 'order_summary' ? (
                <textarea
                  aria-describedby={errors[field] ? `${field}-error` : undefined}
                  aria-invalid={Boolean(errors[field])}
                  name={field}
                  onChange={handleInputChange}
                  value={formData[field]}
                />
              ) : (
                <input
                  aria-describedby={errors[field] ? `${field}-error` : undefined}
                  aria-invalid={Boolean(errors[field])}
                  name={field}
                  onChange={handleInputChange}
                  type="text"
                  value={formData[field]}
                />
              )}
              {errors[field] && (
                <span className="field-error" id={`${field}-error`} role="alert">
                  {errors[field]}
                </span>
              )}
            </label>
          ))}
          <button type="submit">Create order</button>
        </form>
      </section>

      <section aria-labelledby="board-title">
        <div className="board-heading">
          <div>
            <p className="section-label">Kanban board</p>
            <h2 id="board-title">Orders by status</h2>
          </div>
          <p className="mock-notice">Data is stored locally in mock mode.</p>
        </div>

        <div className="board">
          {ORDER_STATUSES.map((status) => {
            const ordersInColumn = orders.filter((order) => order.status === status)

            return (
              <section className="column" key={status} aria-labelledby={`status-${status}`}>
                <div className="column-header">
                  <h3 id={`status-${status}`}>{status}</h3>
                  <span aria-label={`Orders: ${ordersInColumn.length}`}>
                    {ordersInColumn.length}
                  </span>
                </div>

                <div className="card-list">
                  {ordersInColumn.length === 0 ? (
                    <p className="empty-state">No orders</p>
                  ) : (
                    ordersInColumn.map((order) => (
                      <article className="order-card" key={order.order_id}>
                        <dl>
                          <div>
                            <dt>Order ID</dt>
                            <dd>{order.order_id}</dd>
                          </div>
                          <div>
                            <dt>Customer</dt>
                            <dd>{order.customer_name}</dd>
                          </div>
                          <div>
                            <dt>Address</dt>
                            <dd>{order.delivery_address}</dd>
                          </div>
                          <div>
                            <dt>Order summary</dt>
                            <dd>{order.order_summary}</dd>
                          </div>
                          <div>
                            <dt>Current status</dt>
                            <dd>{order.status}</dd>
                          </div>
                        </dl>

                        <label className="move-control">
                          <span>Move to</span>
                          <select
                            aria-label={`Change status for order ${order.order_id}`}
                            onChange={(event) => handleStatusChange(order.order_id, event.target.value)}
                            value={order.status}
                          >
                            {ORDER_STATUSES.map((availableStatus) => (
                              <option key={availableStatus} value={availableStatus}>
                                {availableStatus}
                              </option>
                            ))}
                          </select>
                        </label>
                      </article>
                    ))
                  )}
                </div>
              </section>
            )
          })}
        </div>
      </section>
    </main>
  )
}

export default App
