  var row;
  function start(){
    row = event.target;
  }
  getChildren = () => {
    var e = event;
    e.preventDefault();
    let y = document.getElementById('tabledata').children[0].children;
    var x = Array.prototype.slice.call(y);
    console.log(x)
    x = x.map((i) => {
      return i.children[0].children[0].children[0].text;
    }).map((i) => {
      return i
    })
    console.log(x)
    return x
  }
  getChildren2 = () => {
    var e = event;
    e.preventDefault();
    let y = document.getElementById('tabledata2').children[0].children;
    var x = Array.prototype.slice.call(y);
    console.log(x)
    x = x.map((i) => {
      return i.children[0].children[0].children[0].text;
    }).map((i) => {
      return i
    })
    console.log(x)
    return x
  }
  
  function dragover(){
    var e = event;
    e.preventDefault();

    let children= Array.from(e.target.parentNode.parentNode.children);

    if(children.indexOf(e.target.parentNode)>children.indexOf(row)){
        e.target.parentNode.after(row);
    }else{
      e.target.parentNode.before(row);
    }
  }
  function update(){
    contestId = document.getElementById('contestIdRef').text
    problems = JSON.stringify(getChildren())
    params = {
      'contestId':contestId,
      'problems':problems
    }
    $.post('/admin/editcontestproblems',params)
    .then(() => {
      location.reload()
      $('html,body').scrollTop(0);
    })
    
  }

/* edit contests in contest groups */
  function updateGroup(){
    contestGroupId = document.getElementById('contestGroupRef').text
    contests = JSON.stringify(getChildren())
    params = {
      'contestGroupId':contestGroupId,
      'contests':contests
    }
    $.post('/admin/editcontestgroupcontests',params)
    .then(() => {
      location.reload()
      $('html,body').scrollTop(0);
    })
    
  }

/* edit groups in contest groups*/
  function updateGroup2(){
    contestGroupId = document.getElementById('contestGroupRef').text
    groups = JSON.stringify(getChildren2())
    params = {
      'contestGroupId':contestGroupId,
      'contestGroups':groups
    }
    $.post('/admin/editcontestgroupgroups',params)
    .then(() => {
      location.reload()
      $('html,body').scrollTop(0);
    })
    
  }
