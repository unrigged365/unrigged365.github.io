/* ===================================================================
 * Keep It Simple 3.0.0 - Main JS
 *
 * ------------------------------------------------------------------- */

(function($) {

    "use strict";
    
    const cfg = {
                scrollDuration : 800, // smoothscroll duration
                mailChimpURL   : ''   // mailchimp url
                };
    const $WIN = $(window);


    // Add the User Agent to the <html>
    // will be used for IE10/IE11 detection (Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; rv:11.0))
    const doc = document.documentElement;
    doc.setAttribute('data-useragent', navigator.userAgent);



   /* preloader
    * -------------------------------------------------- */
    const ssPreloader = function() {

        $("html").addClass('ss-preload');

        $WIN.on('load', function() {

            // force page scroll position to top at page refresh
            // $('html, body').animate({ scrollTop: 0 }, 'normal');

            // will first fade out the loading animation 
            $("#loader").fadeOut("slow", function() {
                // will fade out the whole DIV that covers the website.
                $("#preloader").delay(300).fadeOut("slow");
            }); 
            
            // for hero content animations 
            $("html").removeClass('ss-preload');
            $("html").addClass('ss-loaded');

        });
    };


    /* mobile menu
    * ---------------------------------------------------- */ 
    const ssMobileMenu = function() {

        const $toggleButton = $('.header-menu-toggle');
        const $headerContent = $('.header-content');
        const $siteBody = $("body");

        $toggleButton.on('click', function(event){
            event.preventDefault();
            
            // at 800px and below
            if (window.matchMedia('(max-width: 800px)').matches) {
                $toggleButton.toggleClass('is-clicked');
                $siteBody.toggleClass('menu-is-open');
            }
        });

        
        $WIN.on('resize', function() {

            // above 800px
            if (window.matchMedia('(min-width: 801px)').matches) {
                if ($siteBody.hasClass("menu-is-open")) $siteBody.removeClass("menu-is-open");
                if ($toggleButton.hasClass("is-clicked")) $toggleButton.removeClass("is-clicked");
            }
        });

        // open (or close) submenu items in mobile view menu. 
        // close all the other open submenu items.
        $('.s-header__nav .has-children').children('a').on('click', function (e) {
            e.preventDefault();

            // at 800px and below
            if (window.matchMedia('(max-width: 800px)').matches) {

                $(this).toggleClass('sub-menu-is-open')
                    .next('ul')
                    .slideToggle(200)
                    .end()
                    .parent('.has-children')
                    .siblings('.has-children')
                    .children('a')
                    .removeClass('sub-menu-is-open')
                    .next('ul')
                    .slideUp(200);

            }
        });

    };


   /* alert boxes
    * ------------------------------------------------------ */
    const ssAlertBoxes = function() {

        $('.alert-box').on('click', '.alert-box__close', function() {
            $(this).parent().fadeOut(500);
        }); 

    };

    
   /* smooth scrolling
    * ------------------------------------------------------ */
    const ssSmoothScroll = function() {
        
        $('.smoothscroll').on('click', function (e) {
            const target = this.hash;
            const $target = $(target);
            
            e.preventDefault();
            e.stopPropagation();

            $('html, body').stop().animate({
                'scrollTop': $target.offset().top
            }, cfg.scrollDuration, 'swing').promise().done(function () {
                window.location.hash = target;
            });
        });

    };


   /* back to top
    * ------------------------------------------------------ */
    const ssBackToTop = function() {
        
        const pxShow = 800;
        const $goTopButton = $(".ss-go-top")

        // Show or hide the button
        if ($(window).scrollTop() >= pxShow) $goTopButton.addClass('link-is-visible');

        $(window).on('scroll', function() {
            if ($(window).scrollTop() >= pxShow) {
                if(!$goTopButton.hasClass('link-is-visible')) $goTopButton.addClass('link-is-visible')
            } else {
                $goTopButton.removeClass('link-is-visible')
            }
        });
    };



   /* Category Filtering
    * ------------------------------------------------------ */
    const ssCategoryFilter = function() {

        // Get URL parameter
        function getURLParameter(name) {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(name);
        }

        // Filter articles by category
        function filterArticles(category) {
            const articles = document.querySelectorAll('.entry');
            let visibleCount = 0;

            articles.forEach(article => {
                if (category === 'all' || article.getAttribute('data-category') === category) {
                    article.style.display = 'block';
                    visibleCount++;
                } else {
                    article.style.display = 'none';
                }
            });

            // Update filter status
            const filterStatus = document.getElementById('filter-status');
            const filterText = document.getElementById('filter-text');

            if (filterStatus && filterText) {
                if (category === 'all') {
                    filterStatus.style.display = 'none';
                } else {
                    const categoryName = category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    filterText.textContent = `Filtering by ${categoryName} (${visibleCount} articles)`;
                    filterStatus.style.display = 'block';
                }
            }

            // Update page nav text
            const pageNav = document.querySelector('.post-list-nav span');
            if (pageNav) {
                if (category === 'all') {
                    pageNav.textContent = 'Showing all 11 articles';
                } else {
                    const categoryName = category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
                    pageNav.textContent = `Showing ${visibleCount} ${categoryName} articles`;
                }
            }
        }

        // Set up category links
        function setupCategoryLinks() {
            const categoryLinks = document.querySelectorAll('a[href*="category="]');
            categoryLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const url = new URL(this.href);
                    const category = url.searchParams.get('category');

                    // Check if we're on catalog.html
                    const currentPage = window.location.pathname.split('/').pop();

                    if (currentPage === 'catalog.html') {
                        // Update URL without page reload
                        const newUrl = category === 'all' ? 'catalog.html' : `catalog.html?category=${category}`;
                        window.history.pushState({}, '', newUrl);

                        // Filter articles
                        filterArticles(category);
                    } else {
                        // Redirect to catalog.html with category parameter
                        const newUrl = category === 'all' ? 'catalog.html' : `catalog.html?category=${category}`;
                        window.location.href = newUrl;
                    }
                });
            });
        }

        // Initialize on page load
        function init() {
            const category = getURLParameter('category') || 'all';
            filterArticles(category);
            setupCategoryLinks();
        }

        // Handle browser back/forward
        window.addEventListener('popstate', function() {
            const category = getURLParameter('category') || 'all';
            filterArticles(category);
        });

        init();
    };

   /* initialize
    * ------------------------------------------------------ */
    (function ssInit() {

        ssPreloader();
        ssMobileMenu();
        ssAlertBoxes();
        ssSmoothScroll();
        ssBackToTop();
        ssCategoryFilter();

    })();

})(jQuery);