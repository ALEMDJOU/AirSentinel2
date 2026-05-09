import { initializeApp, getApps } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

const firebaseConfig = {
  apiKey: "AIzaSyBWMKj5_RWh3dquFV-3zNTspcY8Bou_y2w",
  authDomain: "airsentinelproject.firebaseapp.com",
  projectId: "airsentinelproject",
  storageBucket: "airsentinelproject.firebasestorage.app",
  messagingSenderId: "581430081327",
  appId: "1:581430081327:web:31131aef57d4976c7b13da",
  measurementId: "G-LCNB7WV64V"
};

// Initialize Firebase only if not already initialized
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export const getFcmToken = async () => {
  try {
    const messaging = getMessaging(app);
    const token = await getToken(messaging, {
      vapidKey: "BCOhvQLvI5jxno6kfSATjGtotNS-ratoHpGgG0O7lTfmHP_utjn1a2CbgGjOEmmN6o6ZgwfhU0wRtceWfbQ95Lg"
    });
    return token;
  } catch (error) {
    console.error("Erreur lors de la récupération du token FCM:", error);
    return null;
  }
};

export const onMessageListener = () =>
  new Promise((resolve) => {
    const messaging = getMessaging(app);
    onMessage(messaging, (payload) => {
      resolve(payload);
    });
  });

export default app;
