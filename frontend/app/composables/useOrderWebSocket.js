import { ref, onMounted, onUnmounted } from 'vue'

export const useOrderWebSocket = (onOrderUpdate) => {
  let ws = null
  const connected = ref(false)
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5

  const connect = () => {
    const config = useRuntimeConfig()
    const wsBaseUrl = config.public.apiBaseUrl.replace('http://', 'ws://').replace('https://', 'wss://')
    const wsUrl = `${wsBaseUrl}/ws/orders/`

    console.log('Connecting to WebSocket:', wsUrl)

    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
      connected.value = true
      reconnectAttempts.value = 0
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('WebSocket message:', data)

        if (onOrderUpdate) {
          onOrderUpdate(data)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason)
      connected.value = false

      // Attempt to reconnect
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.value), 10000)
        console.log(`Reconnecting in ${delay}ms... (attempt ${reconnectAttempts.value}/${maxReconnectAttempts})`)
        setTimeout(connect, delay)
      } else {
        console.error('Max reconnection attempts reached')
      }
    }
  }

  const disconnect = () => {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  onMounted(() => {
    connect()
  })

  onUnmounted(() => {
    disconnect()
  })

  return {
    connected,
    disconnect,
    reconnect: connect
  }
}