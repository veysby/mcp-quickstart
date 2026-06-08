import { ChatKit, useChatKit } from '@openai/chatkit-react'

export default function App() {
  const { control } = useChatKit({
    api: {
      url: '/chatkit',
      domainKey: 'local-dev',
    },
    composer: {
      tools: [
        { id: 'echo', label: 'Echo', icon: 'bolt', placeholderOverride: 'Type something to echo...', persistent: true },
        { id: 'weather', label: 'Weather', icon: 'globe', placeholderOverride: 'Ask about the weather...', persistent: true },
      ],
    },
  })

  return (
    <div style={{ height: '100dvh', display: 'flex', flexDirection: 'column' }}>
      <ChatKit control={control} style={{ flex: 1 }} />
    </div>
  )
}
