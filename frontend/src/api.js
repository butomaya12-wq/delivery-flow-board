// MOCK / TEMPORARY: replace this module with a real API client when a backend exists.
const STORAGE_KEY = 'delivery-flow-board.mock-orders.v1'

export const ORDER_STATUSES = ['New', 'Preparing', 'Out for delivery', 'Delivered']

const LEGACY_STATUS_MAP = {
  Новый: 'New',
  Готовится: 'Preparing',
  'В доставке': 'Out for delivery',
  Доставлен: 'Delivered',
}

function readOrders() {
  try {
    const storedOrders = JSON.parse(window.localStorage.getItem(STORAGE_KEY) ?? '[]')

    if (!Array.isArray(storedOrders)) {
      return []
    }

    const migratedOrders = storedOrders.map((order) => {
      const migratedStatus = LEGACY_STATUS_MAP[order?.status]

      return migratedStatus ? { ...order, status: migratedStatus } : order
    })

    if (migratedOrders.some((order, index) => order !== storedOrders[index])) {
      saveOrders(migratedOrders)
    }

    return migratedOrders.filter(isValidOrder)
  } catch {
    return []
  }
}

function isValidOrder(order) {
  return (
    typeof order?.order_id === 'string' &&
    typeof order.customer_name === 'string' &&
    typeof order.delivery_address === 'string' &&
    typeof order.order_summary === 'string' &&
    ORDER_STATUSES.includes(order.status)
  )
}

function saveOrders(orders) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(orders))
}

function generateOrderId(orders) {
  let orderId

  do {
    const identifier =
      typeof crypto?.randomUUID === 'function'
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`
    orderId = `ORD-${identifier}`
  } while (orders.some((order) => order.order_id === orderId))

  return orderId
}

function validateOrderInput(orderInput) {
  const requiredFields = ['customer_name', 'delivery_address', 'order_summary']

  for (const field of requiredFields) {
    if (!orderInput[field]?.trim()) {
      throw new Error(`Required field is missing: ${field}`)
    }
  }
}

export function listOrders() {
  return readOrders()
}

export function createOrder(orderInput) {
  validateOrderInput(orderInput)

  const orders = readOrders()
  const order = {
    order_id: generateOrderId(orders),
    customer_name: orderInput.customer_name.trim(),
    delivery_address: orderInput.delivery_address.trim(),
    order_summary: orderInput.order_summary.trim(),
    status: 'New',
  }

  saveOrders([...orders, order])
  return order
}

export function updateOrderStatus(orderId, status) {
  if (!ORDER_STATUSES.includes(status)) {
    throw new Error('Unsupported order status')
  }

  const orders = readOrders()
  const orderExists = orders.some((order) => order.order_id === orderId)

  if (!orderExists) {
    throw new Error('Order not found')
  }

  const updatedOrders = orders.map((order) =>
    order.order_id === orderId ? { ...order, status } : order,
  )

  saveOrders(updatedOrders)
  return updatedOrders.find((order) => order.order_id === orderId)
}
