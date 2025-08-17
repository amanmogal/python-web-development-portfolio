/**
 * Modern Web Application - JavaScript Implementation
 * Demonstrating advanced JavaScript skills and modern web development practices
 */

// Main Application Class
class PortfolioApp {
    constructor() {
        this.currentSection = 'home';
        this.isLoading = false;
        this.notifications = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupIntersectionObserver();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Navigation
        this.setupNavigation();
        
        // Form handling
        this.setupContactForm();
        
        // Smooth scrolling
        this.setupSmoothScrolling();
        
        // Window events
        this.setupWindowEvents();
        
        // Project interactions
        this.setupProjectInteractions();
    }

    setupNavigation() {
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        const navLinks = document.querySelectorAll('.nav-link');

        // Mobile menu toggle
        hamburger?.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu?.classList.toggle('active');
        });

        // Close mobile menu when clicking on links
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                hamburger?.classList.remove('active');
                navMenu?.classList.remove('active');
            });
        });

        // Active navigation highlighting
        window.addEventListener('scroll', () => {
            this.updateActiveNavigation();
        });
    }

    setupContactForm() {
        const contactForm = document.getElementById('contactForm');
        
        contactForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleFormSubmission(e.target);
        });

        // Real-time form validation
        const formInputs = contactForm?.querySelectorAll('input, textarea');
        formInputs?.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    setupSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                
                if (targetSection) {
                    this.scrollToSection(targetSection);
                }
            });
        });
    }

    setupWindowEvents() {
        // Navbar background on scroll
        window.addEventListener('scroll', () => {
            this.handleNavbarScroll();
        });

        // Resize handling
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Loading state management
        window.addEventListener('load', () => {
            this.hideLoading();
        });
    }

    setupProjectInteractions() {
        const projectCards = document.querySelectorAll('.project-card');
        
        projectCards.forEach(card => {
            card.addEventListener('click', () => {
                this.handleProjectClick(card);
            });

            // Hover effects
            card.addEventListener('mouseenter', () => {
                this.animateProjectCard(card, 'enter');
            });

            card.addEventListener('mouseleave', () => {
                this.animateProjectCard(card, 'leave');
            });
        });
    }

    // Navigation Methods
    updateActiveNavigation() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');
        
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (window.pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }

    handleNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        const scrollTop = window.pageYOffset;
        
        if (scrollTop > 100) {
            navbar?.classList.add('scrolled');
        } else {
            navbar?.classList.remove('scrolled');
        }
    }

    // Form Handling Methods
    async handleFormSubmission(form) {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Show loading state
        this.showLoading();
        
        try {
            // Simulate API call
            await this.simulateApiCall(data);
            
            // Show success message
            this.showNotification('Message sent successfully!', 'success');
            
            // Reset form
            form.reset();
            
        } catch (error) {
            this.showNotification('Failed to send message. Please try again.', 'error');
        } finally {
            this.hideLoading();
        }
    }

    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        let isValid = true;
        let errorMessage = '';

        // Remove existing error
        this.clearFieldError(field);

        // Validation rules
        switch (fieldName) {
            case 'name':
                if (value.length < 2) {
                    isValid = false;
                    errorMessage = 'Name must be at least 2 characters long';
                }
                break;
                
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    isValid = false;
                    errorMessage = 'Please enter a valid email address';
                }
                break;
                
            case 'subject':
                if (value.length < 5) {
                    isValid = false;
                    errorMessage = 'Subject must be at least 5 characters long';
                }
                break;
                
            case 'message':
                if (value.length < 10) {
                    isValid = false;
                    errorMessage = 'Message must be at least 10 characters long';
                }
                break;
        }

        if (!isValid) {
            this.showFieldError(field, errorMessage);
        }

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.style.color = '#ef4444';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorDiv = field.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // Animation Methods
    initializeAnimations() {
        // Animate skill bars on scroll
        this.animateSkillBars();
        
        // Typing animation for hero title
        this.initTypingAnimation();
        
        // Parallax effects
        this.initParallaxEffects();
    }

    animateSkillBars() {
        const skillItems = document.querySelectorAll('.skill-item');
        
        skillItems.forEach(item => {
            const progressBar = item.querySelector('.skill-progress');
            if (progressBar) {
                const width = progressBar.style.width;
                progressBar.style.width = '0%';
                
                setTimeout(() => {
                    progressBar.style.width = width;
                }, 500);
            }
        });
    }

    initTypingAnimation() {
        const heroTitle = document.querySelector('.hero-title');
        if (!heroTitle) return;

        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        // Start typing animation after a delay
        setTimeout(typeWriter, 1000);
    }

    initParallaxEffects() {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.parallax');
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.speed || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        const animateElements = document.querySelectorAll('.project-card, .skill-item, .contact-info');
        animateElements.forEach(el => observer.observe(el));
    }

    // Utility Methods
    scrollToSection(section) {
        const offsetTop = section.offsetTop - 70; // Account for fixed navbar
        
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }

    showLoading() {
        this.isLoading = true;
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay?.classList.add('active');
    }

    hideLoading() {
        this.isLoading = false;
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay?.classList.remove('active');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const container = document.getElementById('notificationContainer');
        container?.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    async simulateApiCall(data) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simulate random success/failure
        if (Math.random() > 0.1) {
            return { success: true };
        } else {
            throw new Error('Network error');
        }
    }

    handleProjectClick(card) {
        const projectTitle = card.querySelector('.project-title')?.textContent;
        this.showNotification(`Opening ${projectTitle}...`, 'info');
        
        // Simulate project opening
        setTimeout(() => {
            this.showNotification(`${projectTitle} opened successfully!`, 'success');
        }, 1000);
    }

    animateProjectCard(card, action) {
        if (action === 'enter') {
            card.style.transform = 'translateY(-10px) scale(1.02)';
        } else {
            card.style.transform = 'translateY(0) scale(1)';
        }
    }

    handleResize() {
        // Handle responsive behavior
        const isMobile = window.innerWidth <= 768;
        
        if (isMobile) {
            document.body.classList.add('mobile');
        } else {
            document.body.classList.remove('mobile');
        }
    }

    async loadInitialData() {
        // Simulate loading initial data
        this.showLoading();
        
        try {
            await new Promise(resolve => setTimeout(resolve, 1500));
            this.hideLoading();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.hideLoading();
        }
    }
}

// Utility Functions
function downloadResume() {
    // Simulate resume download
    const link = document.createElement('a');
    link.href = '#';
    link.download = 'resume.pdf';
    link.textContent = 'Download Resume';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show notification
    app.showNotification('Resume download started!', 'success');
}

// Global scroll function
function scrollToSection(sectionId) {
    const section = document.querySelector(sectionId);
    if (section) {
        app.scrollToSection(section);
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.init();
    }

    init() {
        this.measurePageLoad();
        this.measureInteractions();
    }

    measurePageLoad() {
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            this.metrics.pageLoadTime = loadTime;
            console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
        });
    }

    measureInteractions() {
        let interactionCount = 0;
        
        document.addEventListener('click', () => {
            interactionCount++;
            this.metrics.interactions = interactionCount;
        });
    }
}

// Error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    app.showNotification('An error occurred. Please refresh the page.', 'error');
});

// Initialize application
let app;
let performanceMonitor;

document.addEventListener('DOMContentLoaded', () => {
    app = new PortfolioApp();
    performanceMonitor = new PerformanceMonitor();
    
    console.log('Portfolio application initialized successfully!');
});

// Service Worker registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export for global access
window.PortfolioApp = PortfolioApp;
window.app = app;