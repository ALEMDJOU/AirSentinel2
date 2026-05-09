importScripts("https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js");

const firebaseConfig = {
  apiKey: "AIzaSyBWMKj5_RWh3dquFV-3zNTspcY8Bou_y2w",
  authDomain: "airsentinelproject.firebaseapp.com",
  projectId: "airsentinelproject",
  storageBucket: "airsentinelproject.firebasestorage.app",
  messagingSenderId: "581430081327",
  appId: "1:581430081327:web:31131aef57d4976c7b13da",
  measurementId: "G-LCNB7WV64V"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log("[firebase-messaging-sw.js] Message reçu en arrière-plan ", payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: "/icons/icon-192x192.png" // Assurez-vous que cette icône existe
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
