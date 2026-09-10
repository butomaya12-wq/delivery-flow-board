const API_BASE_URL = 'http://localhost:8000'

export const ORDER_STATUSES = ['New', 'Preparing', 'Out for delivery', 'Delivered']

async function request(path, options = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options)
  } catch {
    throw new Error('Unable to reach the backend.')
  }

  if (!response.ok) {
    const responseBody = await response.json().catch(() => null)
    const message =
      typeof responseBody?.detail === 'string'
        ? responseBody.detail
        : `Request failed with status ${response.status}.`

    throw new Error(message)
  }

  return response.json()
}

export function listOrders() {
  return request('/api/orders')
}

export function createOrder({ customer_name, delivery_address, order_summary }) {
  return request('/api/orders', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customer_name, delivery_address, order_summary }),
  })
}

export function updateOrderStatus(orderId, status) {
  return request(`/api/orders/${encodeURIComponent(orderId)}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
}
