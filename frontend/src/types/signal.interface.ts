export interface CustomSignal {
    name: string
	join_time: number
    active_time: number
    burn_chance: number
    profit_percent: number
}

export type RandomSignal = {
    name: string
}

export type ActiveSignals = {
    active_signals: ActiveSignal[]
}

interface ActiveSignal {
    signal_id: number
    name: string
    join_until: Date
    expires_at: Date
}

export interface JoinSignal {
    telegram_id: number,
    signal_id: number,
    amount: number
}