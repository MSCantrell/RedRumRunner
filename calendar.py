class Calendar:
    """
    Tracks game time with days, months, and years.
    """
    def __init__(self, day=1, month=1, year=1):
        self.day = day
        self.month = month
        self.year = year
        self.days_per_month = 30  # Simplified calendar
        self.months_per_year = 12
        self.total_days = 0  # Total days elapsed
    
    def reset(self):
        """Reset the calendar to day 1, month 1, year 1."""
        self.day = 1
        self.month = 1
        self.year = 1
        self.total_days = 0
    
    def advance(self, days=1):
        """
        Advance the calendar by a specified number of days.
        
        Args:
            days (int): Number of days to advance.
            
        Returns:
            tuple: (days_elapsed, months_elapsed, years_elapsed)
        """
        days_elapsed = 0
        months_elapsed = 0
        years_elapsed = 0
        
        self.total_days += days
        self.day += days
        
        # Handle month overflow
        while self.day > self.days_per_month:
            self.day -= self.days_per_month
            self.month += 1
            months_elapsed += 1
            
            # Handle year overflow
            if self.month > self.months_per_year:
                self.month = 1
                self.year += 1
                years_elapsed += 1
        
        days_elapsed = days
        
        return (days_elapsed, months_elapsed, years_elapsed)
    
    def get_season(self):
        """
        Get the current season.
        
        Returns:
            str: "winter", "spring", "summer", or "fall"
        """
        if 3 <= self.month <= 5:
            return "spring"
        elif 6 <= self.month <= 8:
            return "summer"
        elif 9 <= self.month <= 11:
            return "fall"
        else:
            return "winter"
    
    def is_special_date(self):
        """
        Check if the current date is a special date in the game world.
        
        Returns:
            tuple: (bool, str) - (is_special, description)
        """
        # Example special dates
        if self.month == 1 and self.day == 1:
            return (True, "New Year's Day")
        elif self.month == 6 and self.day == 15:
            return (True, "Midsummer Festival")
        elif self.month == 12 and self.day == 25:
            return (True, "Winter Solstice")
        
        return (False, "")
    
    def to_string(self):
        """
        Get a string representation of the date.
        
        Returns:
            str: Date string.
        """
        return f"Day {self.day}, Month {self.month}, Year {self.year}"
    
    def to_dict(self):
        """
        Convert to a dictionary for serialization.
        
        Returns:
            dict: Dictionary representation.
        """
        return {
            "day": self.day,
            "month": self.month,
            "year": self.year,
            "total_days": self.total_days
        }
    
    @staticmethod
    def from_dict(data):
        """
        Create a Calendar from a dictionary.
        
        Args:
            data (dict): Dictionary representation.
            
        Returns:
            Calendar: New Calendar instance.
        """
        calendar = Calendar(
            day=data.get("day", 1),
            month=data.get("month", 1),
            year=data.get("year", 1)
        )
        calendar.total_days = data.get("total_days", 0)
        return calendar
