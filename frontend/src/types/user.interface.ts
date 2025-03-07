export interface User {
    id: number
    telegram_id: number
    username: string
    first_name: string
    last_name: string
    language_code: string
    photo_url: string
    created_at: Date
    updated_at: Date
    is_bot: boolean
}