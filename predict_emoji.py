class model_emoji(object):
    
    def __init__(self):
        np.random.seed(1)
        self.X = tweets_df['tweets'].values
        self.y = tweets_df['emoji']
        self.stopwords = set(list(ENGLISH_STOP_WORDS) + ['rt', 'follow', 'dm', 'https', 'ur', 'll' ,'amp', 'subscribe', 'don', 've', 'retweet', 'im', 'http','lt'])

    
    def tfidf(self, max_features=10000, max_df = .8, min_df = .001, ngram_range = (1,2)):
        
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=0)
        tfidf = TfidfVectorizer(max_features= max_features, max_df = max_df, min_df = min_df, 
                                stop_words = self.stopwords, ngram_range = ngram_range)
        tfidf.fit(X_train)
        X_train_tfidf = tfidf.transform(X_train)
        X_test_tfidf = tfidf.transform(X_test)
        return(X_train_tfidf, X_test_tfidf)

    def gnb_model(self):

        X_train_tfidf, X_test_tfidf = self.tfidf()
        gnb = naive_bayes.GaussianNB()
        gnb.fit(X_train_tfidf.todense(), y_train)
        predictions_gnb = gnb.predict(X_test_tfidf.todense())
        score = accuracy_score(predictions_gnb, y_test)*100
        print("Gaussian Naive Bayes Accuracy Score -> ", score)
        return(gnb)
                                    
    def sgd_model(self):
        
        X_train_tfidf, X_test_tfidf = self.tfidf()
        sgd = SGDClassifier(loss="log", alpha=.0001, max_iter=50, penalty="elasticnet")
        sgd.fit(X_train_tfidf, y_train)
        # predict the labels on validation dataset
        predictions_sgd = nb.predict(X_test_tfidf)
        # Use accuracy_score function to get the accuracy
        sgd_score = accuracy_score(predictions_sgd, y_test)*100
        print("Stochastic Gradient Descent Accuracy Score -> ", sgd_score)
        return(sgd)
    
    # prediction
    def prediction(self, model, text, top_n = 5):
        test_tfidf = tfidf.transform([text])
        if model == gnb:
            probs = model.predict_proba(test_tfidf.todense())
            predict_rank = pd.DataFrame({type(model).__name__+' predictions': gnb.classes_, 'probs': probs[0]})
            predict_rank = predict_rank[predict_rank['probs']>0]
            predict_rank = predict_rank.sort_values(by = 'probs', ascending = False)

        else:
            probs = model.predict_proba(test_tfidf.todense())
            predict_rank = pd.DataFrame({type(model).__name__+' predictions': model.classes_, 'probs': probs[0]})
            predict_rank = predict_rank.sort_values(by = 'probs', ascending = False)

        return(predict_rank[:top_n].reset_index(drop=True)) 


    def print_prediction(self, models, text, top_n = 5):
        
        df = pd.DataFrame()
        for i in models:
            df = pd.concat([df, prediction(i, text, top_n)], axis=1)
        print('top {} predictions for {} is:'.format(top_n, text))
        return(df)
    
if __name__ == '__main__':
    
    emoji = model_emoji()
    models = [emoji.gnb_model(), emoji.sgd_model()]