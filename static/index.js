const inputBtn = document.getElementById("inputBtn");
const inputContent = document.getElementById("inputContent");

async function get_message(){
    try{
        const response = await fetch("/api/message",{
            method:"GET"
        })
        const result = await response.json();
        console.log(result);
        return result;
    }catch(error){
        console.log(error);
    }
}

async function render_message(){
    const response = await get_message();
    const data = response.data;

    if(data.length === 0){
        console.log("暫無資料")
        return;
    }

    let innerhtml = "";
    data.reverse().forEach((msg)=>{
        const user_message = msg.user_message;
        const user_pic = msg.pic_url;

        if(!user_pic){
        innerhtml +=`
        <div class = "line"></div>
        <div>${user_message}</div>
        `
        }else if(!user_message){
        innerhtml +=`
        <div class = "line"></div>
        <img src = "${user_pic}"class = "pic">
        `
        }else{
        innerhtml +=`
        <div class = "line"></div>
        <div>${user_message}</div>
        <img src = "${user_pic}" class = "pic">
        `
        }
    })
    console.log(innerhtml);
    inputContent.innerHTML = innerhtml;
}

render_message();

inputBtn.addEventListener("click",async ()=>{
    const inputpic = document.getElementById("inputpic");
    const inputText = document.getElementById("inputText").value;

    if(!inputpic.files[0] && inputText === ""){
        alert("請輸入留言或圖片");
        return;
    }

    const formData = new FormData();
    formData.append("message",inputText);
    if(inputpic.files[0]){
        const file = inputpic.files[0];

        if(!file.type.startsWith("image/")){
            alert("檔案請上傳圖片");
            document.getElementById("inputpic").value = "";
            return;
        }
        formData.append("image",inputpic.files[0]); 
    }
    try{
        const response = await fetch("/api/message",{
            method:"POST",
            body:formData
        });

        const result = await response.json();
        console.log(result);
        render_message();
        document.getElementById("inputText").value = "";
        document.getElementById("inputpic").value = "";

    }catch(error){
        console.log(error);
    }
})

