'use server'

import { cookies } from "next/headers";


export async function getUserAuthToken() {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('auth');
        return token ? token.value : null;
    } catch (error) {
        console.error('Error retrieving auth token:', error);
        throw error;
    }
}