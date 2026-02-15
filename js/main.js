// Seren Matcha Mock-up JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // ===========================
    // SMOOTH SCROLL
    // ===========================
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

    // ===========================
    // COUNTDOWN TIMER
    // ===========================
    function updateCountdown() {
        // Set end date for limited edition (example: 24 days from now)
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 23);
        endDate.setHours(23, 59, 59);

        function update() {
            const now = new Date().getTime();
            const distance = endDate - now;

            if (distance < 0) {
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            // Update timer display
            const timerUnits = document.querySelectorAll('.timer-unit');
            if (timerUnits.length >= 3) {
                timerUnits[0].querySelector('.timer-value').textContent = days;
                timerUnits[1].querySelector('.timer-value').textContent = hours;
                timerUnits[2].querySelector('.timer-value').textContent = minutes;
            }
        }

        update();
        setInterval(update, 60000); // Update every minute
    }

    updateCountdown();

    // ===========================
    // STICKY NAV ON SCROLL
    // ===========================
    const nav = document.querySelector('.nav');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            nav.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
        } else {
            nav.style.boxShadow = 'none';
        }

        lastScroll = currentScroll;
    });

    // ===========================
    // ADD TO CART SIMULATION
    // ===========================
    const addToCartButtons = document.querySelectorAll('.btn-primary:not(.btn-subscribe):not(.btn-waitlist)');
    const cartButton = document.querySelector('.nav-cart');
    let cartCount = 0;

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.textContent.includes('Add to Cart')) {
                e.preventDefault();
                cartCount++;
                cartButton.textContent = `Cart (${cartCount})`;
                
                // Add animation
                this.textContent = '✓ Added!';
                this.style.background = '#97BC62';
                
                setTimeout(() => {
                    this.textContent = 'Add to Cart';
                    this.style.background = '';
                }, 2000);
            }
        });
    });

    // ===========================
    // SUBSCRIBE BUTTON TOGGLE
    // ===========================
    const subscribeButtons = document.querySelectorAll('.btn-subscribe');
    
    subscribeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productCard = this.closest('.product-card');
            const addToCartBtn = productCard.querySelector('.btn-primary:not(.btn-subscribe)');
            
            if (this.textContent.includes('Subscribe')) {
                // Toggle to one-time
                this.textContent = 'One-Time Purchase';
                this.style.background = '#f5f5f5';
                this.style.color = '#666';
                addToCartBtn.textContent = 'Subscribe - $' + (parseFloat(addToCartBtn.textContent.match(/\d+/)) * 0.85).toFixed(0);
            } else {
                // Toggle back to subscribe
                this.textContent = 'Subscribe & Save 15%';
                this.style.background = '';
                this.style.color = '';
                addToCartBtn.textContent = 'Add to Cart';
            }
        });
    });

    // ===========================
    // WAITLIST MODAL (SIMULATION)
    // ===========================
    const waitlistButtons = document.querySelectorAll('.btn-waitlist');
    
    waitlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productName = this.closest('.product-card').querySelector('.product-name').textContent;
            alert(`Thanks for your interest in ${productName}! \n\nWe'll email you at ${getCurrentUserEmail()} when it's available.\n\n(This is a mock-up - no actual email will be sent)`);
            
            // Update waitlist count
            const waitlistCount = this.parentElement.nextElementSibling;
            if (waitlistCount && waitlistCount.classList.contains('waitlist-count')) {
                const currentCount = parseInt(waitlistCount.textContent.match(/\d+/));
                waitlistCount.textContent = `🔔 ${currentCount + 1} people on waitlist`;
            }
        });
    });

    function getCurrentUserEmail() {
        return 'user@example.com'; // Mock email
    }

    // ===========================
    // PRODUCT CARD HOVER EFFECTS
    // ===========================
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // ===========================
    // MOBILE MENU (BASIC)
    // ===========================
    // Note: Kevin will implement proper mobile menu in Shopify theme
    // This is just a placeholder indicator
    if (window.innerWidth <= 768) {
        const navMenu = document.querySelector('.nav-menu');
        if (navMenu) {
            navMenu.style.display = 'none';
            // In production, add hamburger menu here
        }
    }

    // ===========================
    // CONSOLE MESSAGE
    // ===========================
    console.log('%cSEREN MATCHA MOCK-UP', 'color: #2C5F2D; font-size: 24px; font-weight: bold;');
    console.log('%cThe Third Wave of Matcha 🍵', 'color: #97BC62; font-size: 16px;');
    console.log('');
    console.log('This is a mock-up design built for visualization.');
    console.log('Features to implement in Shopify:');
    console.log('- Product subscription engine');
    console.log('- Waitlist email capture');
    console.log('- Limited edition timer (real-time)');
    console.log('- Instagram feed integration');
    console.log('- Matcha quiz builder');
    console.log('- Review system integration');
    console.log('');
    console.log('Built by OpenClaw 🤖');

});
