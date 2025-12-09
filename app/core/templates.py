class MessageTemplates:
    
    @staticmethod
    def get_initial_outreach(owner_name, property_address):
        """
        Generates the first cold outreach text.
        Constraints: Keep under 160 characters to avoid double-billing segments.
        """
        # Clean the name (e.g., "JAMES FENNER" -> "James")
        if owner_name:
            first_name = owner_name.split()[0].title()
        else:
            first_name = "there"
        
        # Clean address (e.g., "123 MAIN ST, RICHMOND, VA" -> "123 Main St")
        if property_address:
            # Take just the street part, not city/state
            addr_short = property_address.split(',')[0].title()
        else:
            addr_short = "your property"

        # The Template
        # "Hi James, I saw 123 Main St and was wondering if you're interested in selling? - [Your Name]"
        return f"Hi {first_name}, I saw {addr_short} and was wondering if you're interested in selling? - Randy Snider"
