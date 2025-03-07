import { User } from "@/types/user.interface"

export interface Referral {
    id: number
	user_id: number
    telegram_id: number
    referral_link: string
    invited_count: number
    referrer_by: User
    referred_by: User
    invited_users: Referral[]
}

interface ReferralData {
    telegram_id: number
    referred_by: number
}

export interface CheckReferral {
    exists: boolean
	message: string
    referral_data: ReferralData
}