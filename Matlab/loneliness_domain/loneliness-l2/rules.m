function [ fncs ] = rules()
    % DO NOT EDIT
    fncs = l2.getRules();
    for i=1:length(fncs)
        fncs{i} = str2func(fncs{i});
    end
end

%ADD RULES BELOW

%DDR1a Effect of training on regulation ability
function result = ddr1a(trace, params, t)
    result = {};
    
    %If training takes place at the current time point increase the
    %emotion regulation ability
    training = trace(t).training.arg{1};
    if training
        for emotion_regulation_ability = l2.getall(trace, t, 'emotion_regulation_ability', {NaN})
            new_ability = emotion_regulation_ability.arg{1} + params.ability_training;
                
            result = {result{:} {t+1, 'emotion_regulation_ability', {new_ability}}};
        end
        
    %If no training occurs maintain the same emotion regulation ability
    else
        for emotion_regulation_ability = l2.getall(trace, t, 'emotion_regulation_ability', {NaN})
            new_ability = emotion_regulation_ability.arg{1};
            
            result = {result{:} {t+1, 'emotion_regulation_ability', {new_ability}}};
        end
    end
end

%DDR1b Effect of training on expectation about others
function result = ddr1b(trace, params, t)
    result = {};
    
    %If training takes place at the current time point decrease  your
    %expectatoin about others
    training = trace(t).training.arg{1};
    if training
        for expectation_of_others = l2.getall(trace, t, 'expectation_about_others', {NaN})
            new_expectation = expectation_of_others.arg{1} - params.expectation_training;

            result = {result{:} {t+1, 'expectation_about_others', {new_expectation}}};
        end
        
    %If no training occurs maintain the same expectation about others
    else
        for expectation_of_others = l2.getall(trace, t, 'expectation_about_others', {NaN})
            new_expectation = expectation_of_others.arg{1};

            result = {result{:} {t+1, 'expectation_about_others', {new_expectation}}};
        end
    end
end

%DDR2 Effect of activity engagement on social activities
function result = ddr2(trace, params, t)
    result = {};
    
    %Increase the amount of social activities enjoyed by the amount of
    %social activities engaged in.
    for activity_engagement = l2.getall(trace, t, 'activity_engagement', {NaN})
        engagement = activity_engagement.arg{1};
        
        for social_activities = l2.getall(trace, t, 'social_activities', {NaN})
            new_activities = social_activities.arg{1} + engagement;
            
            result = {result{:} {t+1, 'social_activities', {new_activities}}};
        end
    end
end

%DDR3 Effect of level of vulnerability, emotion regulation ability, social
%activities and expectation about others on feeling of loneliness
function result = ddr3(trace, params, t)
    result = {};
    
    for level_of_vulnerability = l2.getall(trace, t, 'level_of_vulnerability', {NaN})
        vulnerability = level_of_vulnerability.arg{1};
        
        for emotion_regulation_ability = l2.getall(trace, t, 'emotion_regulation_ability', {NaN})
            emotion_regulation = emotion_regulation_ability.arg{1};
            
            for expectation_about_others = l2.getall(trace, t, 'expectation_about_others', {NaN})
                expectation = expectation_about_others.arg{1};
                
                for social_activities = l2.getall(trace, t, 'social_activities', {NaN})
                    activities = social_activities.arg{1};
                        
                    %Initialize influence variable to convert the
                    %non-numerical value of level_of_vulnerability to a
                    %numerical value to calculate new_feeling with.
                    influence = 0;
                    
                    if strcmp(vulnerability, 'high')
                        influence = params.vulnerability_high;
                    else
                        influence = params.vulnerability_low;
                    end

                    %Sum value new_feeling is determined by the following
                    %equation.
                    new_feeling = influence + expectation - emotion_regulation - activities;

                    %Initialize loneliness variable (this value is not
                    %used).
                    loneliness = false;

                    %If the sum variable exceeds a certain value set the
                    %feeling of loneliness accordingly.
                    if new_feeling < params.loneliness_threshold
                        loneliness = false;
                    else
                        loneliness = true;
                    end

                    result = {result{:} {t+1, 'feeling_of_loneliness', {loneliness}}};
                end
            end
        end
    end
end

%DDR4a Effect of feeling of loneliness on alcoholism, performance and
%cardiovascular diseases
function result = ddr4a(trace, params, t)
    result = {};
    
    for feeling_of_loneliness = l2.getall(trace, t, 'feeling_of_loneliness', {NaN})
        feeling = feeling_of_loneliness.arg{1};
        
        for performance_measure = l2.getall(trace, t, 'performance', {NaN})
            performance = performance_measure.arg{1};
            
            %Initialize new_performance variable (this value is not used).
            new_performance = 'high';
            
            %If there is a feeling of loneliness the new work performance
            %will be low, otherwise the work performance will be high
            if feeling
                new_performance = 'low';
            else
                new_performace = 'high';
            end              

            result = {result{:} {t+1, 'performance', {new_performance}}};
        end
    end
end

%DDR4b Effect of feeling of loneliness on alcoholism
function result = ddr4b(trace, params, t)
    result = {};
    
    for feeling_of_loneliness = l2.getall(trace, t, 'feeling_of_loneliness', {NaN})
        feeling = feeling_of_loneliness.arg{1};

        for alcoholism_level = l2.getall(trace, t, 'alcoholism', {NaN})
            alcoholism = alcoholism_level.arg{1};
            
            %Initialize the new_alcoholism variable (this value is not actually used)
            new_alcoholism = alcoholism;

            %If there is a feeling of loneliness increase the amount of
            %alcohol that is consumed, otherwise decrease it.
            if feeling
                new_alcoholism = alcoholism * params.alcoholism_increase;
            else
                new_alcoholism = alcoholism * params.alcoholism_decrease;
            end                  

            result = {result{:} {t+1, 'alcoholism', {new_alcoholism}}};
        end
    end
end

%DDR4c Effect of feeling of loneliness on cardiovascular diseases
function result = ddr4c(trace, params, t)
    result = {};
    
    for feeling_of_loneliness = l2.getall(trace, t, 'feeling_of_loneliness', {NaN})
        feeling = feeling_of_loneliness.arg{1};

        diseases = trace(t).cardiovascular_diseases.arg{1};
        
        %Initialize the new_diseases variable (This value is used in case 
        %none of the conditions of the if-statement are true).
        new_diseases = false;

        %If cardiovascular diseases are already present they stay present
        %(not recoverable), otherwise check if there is a feeling of
        %loneliness. If there is a feeling of loneliness cardiovascular
        %diseases are present.
        if diseases
            new_diseases = diseases;
        elseif feeling
            new_diseases = true;
        end              

        result = {result{:} {t+1, 'cardiovascular_diseases', {new_diseases}}};
    end
end




% these rules are used solely to make the plots of predicates more readable
% use these as examples when needed

function result = plotEmotionRegAbility(trace, params, t)
    result = {};
    for e = l2.getall(trace, t, 'emotion_regulation_ability', {NaN})
        val = e.arg{1};
        result = {result{:} {t, 'plotEmotionRegAbility', val}};
    end
end

function result = plotEmotionRegAbilityArnie(trace, params, t)
    result = {};
    for e = l2.getall(trace, t, 'emotion_regulation_ability', {NaN})
        val = e.arg{1};
        result = {result{:} {t, 'plotEmotionRegAbilityArnie', val}};
    end
end


