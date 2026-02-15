// Seren Matcha Website JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Add to Cart Functionality
    const addToCartButtons = document.querySelectorAll('.btn-add-cart');
    let cartCount = 0;
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            cartCount++;
            updateCartDisplay();
            
            // Button feedback
            const originalText = this.textContent;
            this.textContent = 'ADDED ✓';
            this.style.background = '#465c29';
            
            setTimeout(() => {
                this.textContent = originalText;
                this.style.background = '';
            }, 2000);
        });
    });
    
    function updateCartDisplay() {
        const cartLinks = document.querySelectorAll('.nav-link');
        cartLinks.forEach(link => {
            if (link.textContent.includes('CART')) {
                link.textContent = `CART (${cartCount})`;
            }
        });
    }
    
    // Waitlist Modal
    const waitlistButtons = document.querySelectorAll('.btn-waitlist');
    
    waitlistButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productCard = this.closest('.product-card');
            const productName = productCard.querySelector('.product-name').textContent;
            
            const email = prompt(`Join the waitlist for ${productName}\n\nEnter your email:`);
            
            if (email && email.includes('@')) {
                alert(`✓ You're on the list!\n\nWe'll email you at ${email} when ${productName} is back in stock.`);
                this.textContent = 'JOINED WAITLIST ✓';
                this.style.background = '#465c29';
                this.style.color = '#fff';
                this.style.borderColor = '#465c29';
            }
        });
    });
    
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
});
