export const changeDateFormat = (date) => {
  // Original date string
  var originalDateString = date;

  // Create a new Date object from the original date string
  var date = new Date(originalDateString);

  // Define months array for converting month index to month name
  var months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];

  // Get individual date components
  var day = date.getDate();
  var month = months[date.getMonth()];
  var year = date.getFullYear();
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var seconds = date.getSeconds();
  var meridiem = hours >= 12 ? "pm" : "am";
  hours = hours % 12;
  hours = hours ? hours : 12; // Handle midnight (0 hours)

  // Format the date string
  var formattedDateString = `${day}-${month}-${year} ${hours}:${minutes}:${seconds} ${meridiem}`;

  return formattedDateString;
};
