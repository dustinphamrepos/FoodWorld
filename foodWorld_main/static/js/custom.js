let autocomplete;

function initAutocomplete() {
  autocomplete = new google.maps.places.Autocomplete(
    document.getElementById("id_address"),
      {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['vn']},
    }
  )

  // function to specify what should happen when the prediction is clicked
  autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged() {
  var place = autocomplete.getPlace();

  // user did not select the prediction. Reset the input field or alert()
  if (!place.geometry) {
    document.getElementById("id_address").placeholder = "Start typing...";
  }
  else {
    //console.log('place name =>', place.name)
  }
  //get the address components and assign them to the fields
  console.log(place);
  var geocoder = new google.maps.Geocoder();
  var address = document.getElementById("id_address").value;
  
  geocoder.geocode({ 'address': address }, function (results, status) {
    console.log('results =>', results);
    //console.log('status =>', status);
    if (status == google.maps.GeocoderStatus.OK) {
      var latitude = results[0].geometry.location.lat();
      var longitude = results[0].geometry.location.lng();

      //console.log('latitude', latitude, 'longitude', longitude);
      $("#id_latitude").val(latitude);
      $("#id_longitude").val(longitude);
      $("#id_address").val(address);
    }
  });
  // Loop through the address components and assign them to the fields
  //console.log(address);
  //console.log(place.address_components);
  for (var i = 0; i < place.address_components.length; i++) {
    for (var j = 0; j < place.address_components[i].types.length; j++) {
      // get country
      if (place.address_components[i].types[j] == 'country') {
        $("#id_country").val(place.address_components[i].long_name)
      }
      // get city
      if (place.address_components[i].types[j] == 'administrative_area_level_1') {
        $("#id_city").val(place.address_components[i].long_name)
      }
      // get district
      if (place.address_components[i].types[j] == 'administrative_area_level_2') {
        $("#id_district").val(place.address_components[i].long_name);
      }
      //console.log(place.address_components);
      // get PIN code
      if (place.address_components[i].types[j] == 'postal_code') {
        $("#id_pin_code").val(place.address_components[i].long_name);
      }
      else {
        $("#id_pin_code").val("")
      }
    }
  }
}

$(document).ready(function () {
  // Add to cart
  $('.add-to-cart').on('click', function (e) {
    e.preventDefault();
    
    var food_item_id = $(this).attr('data-id');
    var url = $(this).attr('data-url');
    //console.log(url);

    $.ajax({
      type: 'GET',
      url: url,
      success: function (response) {
        console.log(response);
        if (response.status == 'login_required') {
          Swal.fire(response.message, '', 'info').then(function () {
            window.location = '/accounts/login/';
          })
        } if (response.status == 'Failed') {
          Swal.fire(response.message, '', 'error')
        } else {
          $('#cart-counter').html(response.cart_counter['cart_count']);
          $('#food-item-qty-' + food_item_id).html(response.quantity);
        }
      },
    });
  })

  // Decrease cart
  $('.decrease-cart').on('click', function (e) {
    e.preventDefault();
    
    var food_item_id = $(this).attr('data-id');
    var url = $(this).attr('data-url');
    console.log(url);

    $.ajax({
      type: 'GET',
      url: url,
      success: function (response) {
        console.log(response);
        if (response.status == 'login_required') {
          Swal.fire(response.message, '', 'info').then(function () {
            window.location = '/accounts/login/';
          })
        } if (response.status == 'Failed') {
          Swal.fire(response.message, '', 'error')
        } else {
          $('#cart-counter').html(response.cart_counter['cart_count']);
          $('#food-item-qty-' + food_item_id).html(response.quantity);
        }
      },
    });
  })

  // place the cart item quantity on load
  $('.cart-item-qty').each(function () {
    var the_id = $(this).attr('id');
    var quantity = $(this).attr('data-qty');
    // console.log(quantity)
    $('#' + the_id).html(quantity)
  })
});