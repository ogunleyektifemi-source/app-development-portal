const observer = new IntersectionObserver((entries)=>{

    entries.forEach(entry=>{

        if(entry.isIntersecting){

            entry.target.classList.add("active");

        }

    });

},{
    threshold:0.15
});

document
.querySelectorAll(".reveal,.slide-left,.slide-right,.zoom")
.forEach(el=>observer.observe(el));