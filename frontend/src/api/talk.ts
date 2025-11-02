import axiosInstance from './index'

export interface TalkResponse {
    reply: string;
    audio_file: string
}

export async function postTalk<TalkResponse>(message: string) {
    return axiosInstance.post<TalkResponse>('/talk', {
        message: message,
    }).then((response) => response.data)
}