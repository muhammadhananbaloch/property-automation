class CriteriaMapper:
    """
    Translates human-readable filters into PropertyRadar API Criteria.
    """

    @staticmethod
    def get_location_criteria(state, city=None, zip_code=None):
        """
        Builds the location targeting block.
        """
        criteria = [{"name": "State", "value": [state]}]
        
        if city:
            # API typically expects City names in Uppercase
            criteria.append({"name": "City", "value": [city.upper()]})
        
        if zip_code:
            # ZipFive takes an Array of Integers
            criteria.append({"name": "ZipFive", "value": [int(zip_code)]})
            
        return criteria

    @staticmethod
    def get_strategy_criteria(strategy_name):
        """
        Returns the specific filter rules for a given investment strategy.
        """
        strategies = {
            "tax_delinquent": [
                {"name": "inTaxDelinquency", "value": [1]}
            ],
            "pre_foreclosure": [
                {"name": "ForeclosureStage", "value": ["Preforeclosure", "Preforeclosure-NTS"]}
            ],
            "vacant": [
                {"name": "isSiteVacant", "value": [1]}
            ],
            "absentee": [
                {"name": "isNotSameMailingOrExempt", "value": [1]}
            ],
            "inherited": [
                {"name": "isDeceasedProperty", "value": [1]}
            ],
            # Add more strategies here as needed
        }
        
        return strategies.get(strategy_name, [])

    @staticmethod
    def build_criteria(state, city, strategy):
        """
        Combines Location + Strategy into the final API payload.
        """
        location_rule = CriteriaMapper.get_location_criteria(state, city=city)
        strategy_rule = CriteriaMapper.get_strategy_criteria(strategy)
        
        return location_rule + strategy_rule
