
for(let element of  jQuery("[hover-class]")) {
    element.addEventListener("mouseenter", function() {
        element.classList.add(
            ...element.getAttribute("hover-class").split(" ")
        );
    });
    element.addEventListener("mouseleave", function() {
        element.classList.remove(
            ...element.getAttribute("hover-class").split(" ")
        );
    });
};

for(let element of  jQuery("[css-transition]")) {
    element.style.transition = element.getAttribute("css-transition");
};

for(let element of jQuery("[view-class]")) {
    let margin = "10";
    (new IntersectionObserver(
        (entries, observer) => {
            entries.forEach((entry) => {
                // Each entry describes an intersection change for one observed
                // target element:
                //   entry.boundingClientRect
                //   entry.intersectionRatio
                //   entry.intersectionRect
                //   entry.isIntersecting
                //   entry.rootBounds
                //   entry.target
                //   entry.time
                let cls = element.getAttribute("view-class");

                if(!cls) return;


                cls = cls.split(" ");
                if(cls[0].endsWith(":")) {
                    [margin, ...cls] = cls;
                    margin = margin.slice(0,-1);
                }
                let ncls = cls.filter((c) => c.startsWith("!"));
                cls = cls.filter((c) => !c.startsWith("!"));
                for(var i = 0; i < ncls.length; i++) ncls[i] = ncls[i].slice(1);
                
                                
                try {
                    if(entry.isIntersecting) {
                        //console.log("added", ...element.getAttribute("view-class").split(" "));
                        element.classList.add(
                            ...cls
                        );
                        element.classList.remove(
                            ...ncls
                        );
                    } else {
                        //console.log("removed", ...element.getAttribute("view-class").split(" "));
                        element.classList.remove(
                            ...cls
                        );
                        element.classList.add(
                            ...ncls
                        );
                    }
                } catch (e) {
                
                }
                
            });
        },
        {
            root: null,
            rootMargin: margin+"px",
            threshold: [1.0, 0.0],
        },
    )).observe(element);
};


function markdown(text) {
    
}


window.addEventListener('scroll', function() {
    let headerBg = jQuery("#header-back-blurred-div");
    headerBg[0].style.backgroundPositionY = (-(window.pageYOffset).toFixed(0) % 50).toString()+"px";
    let t = window.pageYOffset/50;
    /*if(t > 1) t = 1;
    headerBg[0].style.opacity = t.toFixed(2).toString()*/
    if(t > 1) headerBg[0].style.opacity = 1
        else headerBg[0].style.opacity = 0
    let elts = jQuery("[onviewbg]")
    for(let i = elts.length - 1; i >= 0; i--) {
        let element = elts[i];
        if(window.pageYOffset >= element.offsetTop + 350) {
            element.parentElement.style.transition = "1s",
            element.parentElement.style.backgroundColor = element.getAttribute('onviewbg');
            break;
        }
    };
});
