// Helper for displaying status messages.
const addMessage = (message) => {
  const messagesDiv = document.querySelector('#messages');
  messagesDiv.style.display = 'block';
  const messageWithLinks = addDashboardLinks(message);
  messagesDiv.innerHTML += `> ${messageWithLinks}<br>`;
  console.log(`Debug: ${message}`);
};

// Adds links for known Stripe objects to the Stripe dashboard.
const addDashboardLinks = (message) => {
  const piDashboardBase = 'https://dashboard.stripe.com/test/payments';
  const cusDashboardBase = 'https://dashboard.stripe.com/test/customers';

  // Add links for PaymentIntents
  let linkedMessage = message.replace(
    /(pi_(\S*)\b)/g,
    `<a href="${piDashboardBase}/$1" target="_blank">$1</a>`
  );

  // Add links for Customers
  linkedMessage = linkedMessage.replace(
    /(cus_(\S*)\b)/g,
    `<a href="${cusDashboardBase}/$1" target="_blank">$1</a>`
  );

  return linkedMessage;
};
