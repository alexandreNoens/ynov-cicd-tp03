# todo sonarqube

- [ ] Etape 3: preparer la CI pour qualite + tests + couverture XML
- [ ] Etape 3: ajouter la commande de tests avec `coverage.xml`
- [ ] Etape 3: verifier que le seuil de couverture en CI est au moins 70%

- [ ] Etape 4: configurer les parametres Sonar
- [ ] Etape 4: lancer le scan Sonar depuis la pipeline

- [ ] Etape 5: configurer le Quality Gate Sonar
- [ ] Etape 5: imposer `0 bugs`
- [ ] Etape 5: imposer `0 vulnerabilities`
- [ ] Etape 5: imposer `duplication < 3%`
- [ ] Etape 5: imposer `coverage >= 70%`

- [ ] Etape 6: activer la decoration PR (commentaire automatique Sonar dans les PR)
- [ ] Etape 6: verifier que le statut Sonar apparait dans les checks GitHub

- [ ] Etape 7: ouvrir une PR de verification
- [ ] Etape 7: verifier lint + tests + scan Sonar + Quality Gate vert
- [ ] Etape 7: confirmer la presence du commentaire Sonar sur la PR
