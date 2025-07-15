
document.addEventListener('DOMContentLoaded', () => {
    const donutListContainer = document.getElementById('donut-list');

    async function fetchDonuts() {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/donuts');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const donuts = await response.json();
            displayDonuts(donuts);
        } catch (error) {
            console.error('Error fetching donuts:', error);
            donutListContainer.innerHTML = '<p class="error-message">Failed to load donuts. Please try again later.</p>';
        }
    }

    function displayDonuts(donuts) {
        donutListContainer.innerHTML = '';

        if (donuts.length === 0) {
            donutListContainer.innerHTML = '<p class="no-donuts-message">No donuts available yet. Check back soon!</p>';
            return;
        }

        donuts.forEach(donut => {
            const donutCard = document.createElement('div');
            donutCard.classList.add('donut-card');

            const imageUrl = donut.image_url || 'https://placehold.co/128x128/CCCCCC/000000?text=No+Image';

            donutCard.innerHTML = `
                <img src="${imageUrl}" alt="${donut.name}">
                <h3>${donut.name}</h3>
                <p>${donut.description || 'A delightful treat!'}</p>
                <span class="price">$${donut.price.toFixed(2)}</span>
            `;
            donutListContainer.appendChild(donutCard);
        });
    }

    fetchDonuts();
});