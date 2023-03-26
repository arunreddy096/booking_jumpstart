$(document).ready(function() {
    // Hide the multi-event and student-related fields by default
    // $('.multi-event').hide();
    $('.single-event.event-name-single').hide();
    $('.single-event.event-name-multi').hide();
    // $('.form-group.label[for="university"]').hide();
    // $('.form-group.select[name="university"]').hide();
    // $('.single-event p.student').hide();
    $('.form-group.student').show();
    $('.form-group.student').show();

    // When the event type changes, show the corresponding form
    $('#event-type').change(function() {

        if ($(this).val() === 'multi-event') {

            $('.single-event').hide();
            $('.multi-event').show();

        }
        else {
            $('.multi-event').hide();
            $('.single-event').show();
        }
    });

    // When the form is changed, calculate the total price
    $('#booking-form').on('input', function() {
        var total = 0;
        var event_price = 0;
        var isStudent = $('#student').is(':checked');
        var adultTickets = parseInt($('#adult-tickets').val() || 0);
        var childrenTickets = parseInt($('#children-tickets').val() || 0);
        var childrenTicketPrice = 10

        if ($('#event-type').val() === 'multi-event') {
            var eventName = $('#event-name-multi').val();
            // Calculate the price for multi-event

            if (eventName === 'High Ropes & Ziplines') {
                event_price = 40;
            }
            else if (eventName === 'Trampoline Park') {
                event_price = 20;
            }
            else if (eventName === 'Indoor Soccer' || eventName === 'Archery Tag') {
                event_price = 30;
            }
            else if (eventName === 'Escape Rooms') {
                event_price = 25;
            }
        } else {
            var eventName = $('#event-name-single').val();
            // Calculate the price for single-event

            if (eventName === 'Arcade Corner') {
                event_price = 25;
            } else if (eventName === 'Rock Climbing Wall') {
                event_price = 30;
            } else if (eventName === 'Axe Throwing') {
                event_price = 35;
            }
        }
        total += adultTickets * event_price;
        total += childrenTickets * 10;

        if (isStudent) {
            total -= 10;
            $('.form-group.student').show();
            $('.form-group.student').show();

        } else {
            $('.form-group.student').hide();
            $('.form-group.student').hide();

        }

        // Update the total price field
        $('#total-price').val('$' + total);
    });

    // When the student checkbox is clicked, show or hide the university select field
    $('#student').click(function() {
        if ($(this).is(':checked')) {
            $('.single-event.student').show();
            $('.single-event label[for="university"]').show();
            $('.single-event select[name="university"]').show();
            $('.single-event p.student').show();
        } else {
            $('.single-event.student').hide();
            $('.single-event label[for="university"]').hide();
            $('.single-event select[name="university"]').hide();
            $('.single-event p.student').hide();
        }

        // Trigger the input event to calculate the total price on page load
        $('#booking-form').trigger('input');
    });

    flatpickr("#booking-date", {
        enable: [
            {
                from: "today",
                to: new Date().fp_incr(30) // 7 days from now
            }
        ],
        altInput: true,
        altFormat: "F j, Y, l",
        dateFormat: "Y-m-d"
    });
});

// $('#booking-form').submit(function(e) {
//     // Get the values of the required fields and validate them
//     var reservationType = $('#event-type').val();
//     var registrationDate = $('#booking-date').val();
//     var eventName = $('#event-name').val();
//     var eventTime = $('#event-time').val();
//     var student = $('#student').val();
//     var university = $('#university').val();
//     var adult_tickets = $('#adult-tickets').val();
//     var children_tickets = $('#children-ticket').val();
//     var spl_adult_tickets = $('#special-adult-tickets').val();
//     var spl_children_tickets = $('#special-children-ticket').val();
//     var address = $('#address').val();
//     var city = $('#city').val();
//     var province = $('#province').val();
//     var phoneNumber = $('#phone-number').val();
//
//     if (reservationType === 'single-event' &&
//         (eventName === '' ||
//             eventTime === '' ||
//                 student === '' ||
//                 university === ''
//             // address === '' ||
//             // city === '' ||
//             // province === '' ||
//             // phoneNumber === ''
//         )) {
//         // Show an error message and prevent the default form submission behavior
//         alert('Please fill in all the required fields');
//         e.preventDefault();
//         return false;
//     }
//
//     // if (reservationType === 'multi-event' &&
//     //     (address === '' ||
//     //         adult_tickets === '' ||
//     //         children_tickets === '' ||
//     //         spl_adult_tickets === '' ||
//     //         spl_children_tickets === ''
//     //         // city === '' ||
//     //         // province === '' ||
//     //         // phoneNumber === ''
//     //     )) {
//     //     // Show an error message and prevent the default form submission behavior
//     //     alert('Please fill in all the required fields');
//     //     e.preventDefault();
//     //     return false;
//     // }
//
//     // Submit the form if all the required fields are filled
//     return true;
// });


