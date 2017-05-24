// var ims = angular.module("ims", []);
angular.module("ims", []).controller('move_page_ctrl', function($scope,$http,$window){
   $scope.showPartNumbers = true;
   $scope.showPartInfo = false;
   $scope.regex = '\\d+';
   $scope.moveQuantity = 0;
   $scope.comment=" "
   
   $scope.generic = function(){
       $scope.toS = false;
       $scope.toI = false;
       $scope.fromS = false;
       $scope.fromI = false;
       $scope.hideToSupplier = false;
       $scope.From_dropdown="From"   
       $scope.fromBuilding = "Building"
       $scope.fromLocation = "Location"
       $scope.To_dropdown="To"
       $scope.toBuilding = "Building"
   }

   $scope.getParts = function(){
    $scope.generic();
    $scope.parts = [];
    $http({
        method:"GET",
        url:'v1/getpartsname'
    }).then(function(res){
        for (var i = 1; i < res.data.length; i++) {
            $scope.parts.push(parseInt(res.data[i][0].trim()));
        }
        $scope.searchPart = "";
    });
   }

    $scope.displayLocations = function(value){
        $scope.locations = ['Scrap','Production'];
        $scope.toBuilding = value
        $http({
                method:"POST",
                url:'v1/getlocations',
                data:$scope.toBuilding,
            }).then(function(res){
                for (var i = 1; i < res.data.length; i++) {
                    
                    if(res.data[i][0]!=(null || undefined)) $scope.locations.push(res.data[i][0].trim());
                }
                $scope.toLocation = undefined;
        });      
    }

    
    $scope.partOptions = function(part){
        $scope.generic();
        if($scope.showPartInfo) $scope.showPartInfo = false;
        else {
             $http({
                method:"POST",
                url:'v1/getpartinfo',
                data:part, 
            }).then(function(res){
                $scope.partInfo = [];
               // $scope.totalQty = 0;
                 for (var i = 0; i < res.data.length; i++) {
                    if(parseInt(res.data[i][2])>0){
                        $scope.partInfo.push({
                            name: res.data[i][0],
                            location:res.data[i][3],
                            building:res.data[i][5],
                            qty: res.data[i][2]
                        });
           //             $scope.totalQty+=res.data[i][2];
                    }
                }
            });
            $scope.partName = part
            $scope.showPartInfo = true;
            
        }
        if($scope.showPartNumbers) $scope.showPartNumbers = false;
        else $scope.showPartNumbers = true;
    }

    $scope.filterLocations = function(value){
        $scope.fromIndexedLocation = [];
        $scope.fromBuilding = value
        console.log($scope.fromBuilding)
        for(var i = 0; i < $scope.partInfo.length; i++){
            if($scope.partInfo[i].building==$scope.fromBuilding){
                $scope.fromIndexedLocation.push($scope.partInfo[i].location)
            }
        }
    }

    $scope.onSelect = function($model){
        $scope.partOptions($model);
    }

    $scope.showMovesPart = function(){
        if($scope.movesPart) $scope.movesPart = false;
        else $scope.movesPart = true;
        $http({
                method:"GET",
                url:'v1/getbuildings',
            }).then(function(res){
                $scope.buildings = [];
                for (var i = 1; i < res.data.length; i++) {
                    if($scope.buildings.indexOf(res.data[i][0]) == -1) $scope.buildings.push(res.data[i][0]);
                }
            });
    }

    $scope.changeFrom = function(value){
        $scope.From = value
        if($scope.From == "inventory") {$scope.From_dropdown = "Inventory";$scope.fromI = true; $scope.fromS = false;$scope.hideToSupplier=false;}
        if($scope.From == "supplier") {$scope.From_dropdown = "Supplier";$scope.fromS = true; $scope.fromI = false; $scope.hideToSupplier=true;}
        
    }

    $scope.changeTo = function(value){
        $scope.To = value
        if($scope.To == "inventory") {$scopeTo_dropdown="Inventory" ;$scope.toI = true;$scope.toS = false;}
        if($scope.To == "supplier") {$scope.To_dropdown = "Supplier" ;$scope.toS = true;$scope.toI = false;}
    }

    $scope.countAllowedQty = function(){
        $scope.totalQty = 0;
        if($scope.From == "inventory"){
            if($scope.fromBuilding==undefined || $scope.fromLocation==undefined) $scope.disableButton = true;
            else $scope.disableButton = false;
        }

        else if($scope.fromSupplier!=undefined){
            $scope.totalQty = Infinity
        }
        else{
            if($scope.fromSupplier==undefined) $scope.disableButton = true;
            else $scope.disableButton = false;
        }
        
       if($scope.fromLocation!="Production" && $scope.fromLocation!="Scrap"){
            for(var i=0;i<$scope.partInfo.length;i++){
                if($scope.partInfo[i]['building']==$scope.fromBuilding){
                    if($scope.partInfo[i]['location']==$scope.fromLocation) $scope.totalQty=$scope.partInfo[i]['qty']
                    else $scope.totalQty=$scope.partInfo[i]['qty']
                }
            }
        }
        else {
            for(var i=0;i<$scope.partInfo.length;i++){
                if($scope.partInfo[i]['building']==$scope.fromBuilding){
                    $scope.totalQty+=$scope.partInfo[i]['qty']
                }
            }
        }
    }

    $scope.moveParts = function(form){
        console.log(form)
        var flag = false;
        if($scope.From=="inventory" && $scope.To=="inventory"){
            if($scope.fromBuilding==undefined||$scope.fromLocation==undefined||$scope.toBuilding==undefined||$scope.toLocation==undefined) {swal("Failed", "Please fill in accurate details to move parts!", "error"); flag = false;}
            else{
                flag = true;
                var data = {
                    fromB:$scope.fromBuilding,
                    fromL:$scope.fromLocation,
                    toB:$scope.toBuilding,
                    toL:$scope.toLocation,
                    qty:$scope.moveQuantity,
                    partName:$scope.partName,
                    who:sessionStorage.getItem('username'),
                    why:$scope.comment,
                    type:"ItoI"
                }
            }
        }
        else if($scope.From=="inventory" && $scope.To=="supplier"){
            if($scope.fromBuilding==undefined||$scope.fromLocation==undefined||$scope.toSupplier==undefined||$scope.toSupplier=="") {swal("Failed", "Please fill in accurate details to move parts!", "error"); flag = false;}
            else{
                flag = true;
                var data = {
                    fromB:$scope.fromBuilding,
                    fromL:$scope.fromLocation,
                    toS:$scope.toSupplier,
                    qty:$scope.moveQuantity,
                    partName:$scope.partName,
                    who:sessionStorage.getItem('username'),
                    why:$scope.comment,
                    type:"ItoS"
                }
            }
        }

        else if($scope.From=="supplier" && $scope.To=="inventory"){
            if($scope.toBuilding==undefined||$scope.toLocation==undefined||$scope.fromSupplier==undefined||$scope.fromSupplier=="") {swal("Failed", "Please fill in accurate details to move parts!", "error"); flag = false;}
            else{
                flag = true;
                var data = {
                    toB:$scope.toBuilding,
                    toL:$scope.toLocation,
                    fromS:$scope.fromSupplier,
                    qty:$scope.moveQuantity,
                    partName:$scope.partName,
                    who:sessionStorage.getItem('username'),
                    why:$scope.comment,
                    type:"StoI"
                }
            }
        }

        else if($scope.From==undefined || $scope.To==undefined) {swal("Failed", "Please fill in accurate details to move parts!", "error"); flag = false;}

        if(flag && $scope.moveQuantity!=undefined){
            $http({
                method:"POST",
                url:'v1/changepartlocation',
                data:data,
            }).then(function(res){
                if(res.data=="done"){
                    swal("Done", "Part Moved!", "success")
                    $scope.partOptions($scope.partName);
                    $scope.generic();
                    $scope.From="",$scope.To="",$scope.fromBuilding="",$scope.fromLocation="",$scope.toBuilding="",$scope.toLocation="",$scope.moveQuantity=0,$scope.movesPart=false,$scope.comment = "";
                } 
                else if(res.data=="error") swal("Failed", "Please fill in accurate details to move parts!", "error")
            });
        }
        else swal("Failed", "Please fill in accurate details to move parts!", "error")
    }

    $scope.logout = function(){
        sessionStorage.removeItem('username');
        $window.location.href='logout';
    }

    //  $scope.checkAdmin = function(data){
    //     if($scope.username=="admin" && data=="purchasing") $window.location.href='purchasing';
    //     else if($scope.username=="admin" && data=="addpart")$window.location.href='addpart';
    //     else swal("Oops", "It seems you don't have privilege for this section", "error");
    // }
});